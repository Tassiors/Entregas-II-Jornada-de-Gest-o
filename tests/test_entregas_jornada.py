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


def test_form_schema_endpoint(client):
    resp = client.get("/api/v1/entregas-jornada/form-schema")
    assert resp.status_code == 200
    data = resp.json()
    assert "title" in data
    assert "instructions" in data
    assert "acknowledgement" in data
    assert "projects" in data
    assert "periods" in data
    assert len(data["projects"]) == 5
    assert len(data["periods"]) == 6


def test_registro_existente_endpoint(client):
    resp = client.get("/api/v1/entregas-jornada/registro-existente?projeto=0&periodo=0")
    assert resp.status_code in (200, 502)
    if resp.status_code == 200:
        data = resp.json()
        assert "exists" in data


def test_formulario_validation_missing_fields(client):
    # Envio com entrega não concluída ("1") e texto vazio deve falhar na validação (status 400)
    payload_invalid = {
        "projeto": "0",
        "periodo": "0",
        "ent1_conc": "1",
        "ent1_txt": "",  # obrigatório quando não concluída
        "ent2_conc": "1",
        "ent2_txt": "Evolução ok",
    }
    resp = client.post("/api/v1/entregas-jornada/formulario", json=payload_invalid)
    assert resp.status_code == 400
    assert "Entrega 1" in resp.json()["detail"]

    # Envio com entrega concluída ("0") e texto vazio deve ter sucesso (comentários opcionais após conclusão)
    payload_valid_empty_comment = {
        "projeto": "0",
        "periodo": "0",
        "ent1_conc": "0",
        "ent1_txt": "",  # opcional quando concluída
        "ent2_conc": "0",
        "ent2_txt": "",  # opcional quando concluída
    }
    resp_ok = client.post("/api/v1/entregas-jornada/formulario", json=payload_valid_empty_comment)
    assert resp_ok.status_code == 200


def test_formulario_crud_and_cascade_local(client):
    # 1. Cria ou salva formulário para o projeto 0 no período 0 marcando ambas como concluídas ("0")
    payload = {
        "projeto": "0",
        "periodo": "0",
        "ent1_conc": "0",
        "ent1_txt": "Ação B0 finalizada",
        "ent2_conc": "0",
        "ent2_txt": "Ação B0 também finalizada",
    }
    resp_create = client.post("/api/v1/entregas-jornada/formulario", json=payload)
    assert resp_create.status_code == 200
    created_data = resp_create.json()
    assert created_data["status"] == "success"
    form_id = created_data["id"]

    # 2. Leitura por ID
    resp_get = client.get(f"/api/v1/entregas-jornada/formularios/{form_id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["ent1_conc"] == "0"
    assert resp_get.json()["ent2_conc"] == "0"

    # 3. Consulta de registro existente no período subsequente (período 1)
    resp_existente_b1 = client.get("/api/v1/entregas-jornada/registro-existente?projeto=0&periodo=1")
    assert resp_existente_b1.status_code == 200
    data_b1 = resp_existente_b1.json()
    assert "cascade_info" in data_b1
    assert data_b1["cascade_info"]["e1_concluida"] is True
    assert data_b1["cascade_info"]["e2_concluida"] is True
    # O formulário sugere diretamente "0" (concluída) herdado em cascata
    assert data_b1["record"]["ent1_conc"] == "0"
    assert data_b1["record"]["ent2_conc"] == "0"

    # 4. Salva o período 1 com as entregas herdadas e comentários vazios (opcionais)
    payload_b1 = {
        "projeto": "0",
        "periodo": "1",
        "ent1_conc": "0",
        "ent1_txt": "",
        "ent2_conc": "0",
        "ent2_txt": "",
    }
    resp_save_b1 = client.post("/api/v1/entregas-jornada/formulario", json=payload_b1)
    assert resp_save_b1.status_code == 200

    # 5. Verifica detalhamento do projeto e timeline: ambas continuam concluídas no período 1
    resp_proj = client.get("/api/v1/entregas-jornada/projetos/0")
    assert resp_proj.status_code == 200
    proj_detail = resp_proj.json()
    assert proj_detail["e1_done"] is True
    assert proj_detail["e2_done"] is True
    tl_b1 = next((item for item in proj_detail["timeline"] if item["periodo_code"] == "1"), None)
    assert tl_b1 is not None
    assert tl_b1["ent1_status"] == "Concluída"
    assert tl_b1["ent2_status"] == "Concluída"


    # 4. Atualização via PUT
    update_payload = {
        "projeto": "0",
        "periodo": "0",
        "ent1_conc": "0",
        "ent1_txt": "Ação B0 finalizada e revisada",
        "ent2_conc": "0",
        "ent2_txt": "Ação B0 concluída agora",
    }
    resp_put = client.put(f"/api/v1/entregas-jornada/formularios/{form_id}", json=update_payload)
    assert resp_put.status_code == 200

    # 5. Exclusão via DELETE
    resp_del = client.delete(f"/api/v1/entregas-jornada/formularios/{form_id}")
    assert resp_del.status_code == 200
    assert resp_del.json()["status"] == "success"