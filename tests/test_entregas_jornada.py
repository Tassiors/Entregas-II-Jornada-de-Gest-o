import pytest
from src.services.redcap_service import (
    process_records,
    get_project_summary,
    get_project_deliveries_matrix,
    get_bimonthly_status,
    get_project_details,
)


def test_process_records_filters_incomplete():
    raw = [
        {"record_id": "1", "projeto": "0", "periodo": "0", "form_1_complete": "0"},
        {"record_id": "2", "projeto": "0", "periodo": "1", "form_1_complete": "1"},
        {"record_id": "3", "projeto": "0", "periodo": "2", "form_1_complete": "2", "ent1_p1_conc": "0"},
    ]
    processed = process_records(raw)
    assert len(processed) == 1
    assert processed[0]["record_id"] == "3"


def test_summary_calculation():
    records = [
        {"record_id": "1", "projeto": "0", "periodo": "0", "ent1_p1_conc": "0", "ent2_p1_conc": "1"},
        {"record_id": "2", "projeto": "1", "periodo": "1", "ent1_p2_conc": "0", "ent2_p2_conc": "0"},
    ]
    summary = get_project_summary(records)
    assert summary["total_deliveries"] == 4
    assert summary["completed"] == 3
    assert summary["completion_rate"] == 75.0


def test_matrix_calculation():
    records = [
        {"record_id": "1", "projeto": "0", "periodo": "0", "ent1_p1_conc": "0", "ent2_p1_conc": "1"},
    ]
    matrix = get_project_deliveries_matrix(records)
    assert len(matrix) == 5
    p1 = next(p for p in matrix if p["code"] == "P1")
    assert p1["e1_done"] is True
    assert p1["e2_done"] is False


def test_bimonthly_status():
    records = [
        {"record_id": "1", "projeto": "0", "periodo": "0"},
        {"record_id": "2", "projeto": "0", "periodo": "0"},
    ]
    bim = get_bimonthly_status(records, proj_key="0")
    assert len(bim) == 6
    b1 = bim[0]
    assert b1["num_label"] == "B1"
    assert b1["entregue"] is True
    assert b1["count"] == 2


def test_entregas_api_endpoints(client):
    resp = client.get("/api/v1/entregas-jornada/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_deliveries" in data
    assert "completed" in data

    resp_matrix = client.get("/api/v1/entregas-jornada/matrix")
    assert resp_matrix.status_code == 200
    matrix_data = resp_matrix.json()
    assert len(matrix_data) == 5

    resp_bim = client.get("/api/v1/entregas-jornada/bimestres")
    assert resp_bim.status_code == 200
    assert len(resp_bim.json()) == 6

    resp_p0 = client.get("/api/v1/entregas-jornada/projetos/0")
    assert resp_p0.status_code == 200
    p0_data = resp_p0.json()
    assert p0_data["code"] == "P1"

    resp_dash = client.get("/api/v1/entregas-jornada/dashboard")
    assert resp_dash.status_code == 200
    dash_data = resp_dash.json()
    assert "summary" in dash_data
    assert "matrix" in dash_data