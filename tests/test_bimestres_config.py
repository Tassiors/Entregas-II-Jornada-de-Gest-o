import pytest
from src.auth.auth import auth_handler


def get_admin_headers(client):
    login_res = client.post(
        "/api/login",
        data={"username": "admin", "password": "admin"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_get_bimestres_config(client):
    headers = get_admin_headers(client)
    resp = client.get("/api/admin/bimestres-config", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 6
    codes = [item["periodo_code"] for item in data]
    assert codes == ["0", "1", "2", "3", "4", "5"]


def test_unauthorized_and_forbidden_bimestres_config(client):
    # Sem autenticação -> 401
    resp_unauth = client.get("/api/admin/bimestres-config")
    assert resp_unauth.status_code == 401

    # Login como usuário comum (sem perfil de admin)
    login_user = client.post(
        "/api/login",
        data={"username": "joao.silva", "password": "password"}
    )
    if login_user.status_code == 200:
        user_token = login_user.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        resp_forbidden = client.get("/api/admin/bimestres-config", headers=user_headers)
        assert resp_forbidden.status_code == 403


def test_bimestres_status_public_endpoint(client):
    resp = client.get("/api/v1/entregas-jornada/bimestres-status")
    assert resp.status_code == 200
    data = resp.json()
    assert "0" in data
    assert "ativo" in data["0"]


def test_admin_disable_bimestre_blocks_new_submission(client):
    admin_headers = get_admin_headers(client)

    # 1. Admin desabilita o período 4
    resp_put = client.put(
        "/api/admin/bimestres-config/4",
        json={"ativo": False},
        headers=admin_headers,
    )
    assert resp_put.status_code == 200
    assert resp_put.json()["ativo"] is False

    # 2. Tentativa de novo preenchimento no período 4 para um projeto sem envio prévio (projeto 3)
    payload_novo = {
        "projeto": "3",
        "periodo": "4",
        "ent1_conc": "0",
        "ent1_txt": "",
        "ent2_conc": "0",
        "ent2_txt": "",
    }
    resp_post = client.post("/api/v1/entregas-jornada/formulario", json=payload_novo, headers=admin_headers)
    assert resp_post.status_code == 400
    assert "fechado para novos preenchimentos" in resp_post.json()["detail"]

    # 3. Restaura o período 4 para ativo
    resp_restore = client.put(
        "/api/admin/bimestres-config/4",
        json={"ativo": True},
        headers=admin_headers,
    )
    assert resp_restore.status_code == 200
    assert resp_restore.json()["ativo"] is True


def test_survival_of_existing_report_on_disabled_bimestre(client):
    admin_headers = get_admin_headers(client)

    # 1. Garante que o período 5 está ativo
    client.put("/api/admin/bimestres-config/5", json={"ativo": True}, headers=admin_headers)

    # 2. Cria relatório para projeto 2 no período 5
    payload = {
        "projeto": "2",
        "periodo": "5",
        "ent1_conc": "0",
        "ent1_txt": "Entrega 1 P3 realizada",
        "ent2_conc": "1",
        "ent2_txt": "Entrega 2 P3 em andamento",
    }
    resp_create = client.post("/api/v1/entregas-jornada/formulario", json=payload, headers=admin_headers)
    assert resp_create.status_code == 200
    created_id = resp_create.json()["id"]

    # 3. Admin desabilita o período 5
    resp_disable = client.put("/api/admin/bimestres-config/5", json={"ativo": False}, headers=admin_headers)
    assert resp_disable.status_code == 200
    assert resp_disable.json()["ativo"] is False

    # 4. Verifica que /bimestres-status informa que o projeto 2 tem submissão e can_fill=True
    resp_status = client.get("/api/v1/entregas-jornada/bimestres-status?projeto=2")
    assert resp_status.status_code == 200
    st_p5 = resp_status.json()["5"]
    assert st_p5["ativo"] is False
    assert st_p5["has_submission"] is True
    assert st_p5["can_fill"] is True

    # 5. Leitura do relatório submetido permanece operacional
    resp_read = client.get(f"/api/v1/entregas-jornada/formularios/{created_id}")
    assert resp_read.status_code == 200
    assert resp_read.json()["ent1_txt"] == "Entrega 1 P3 realizada"

    # 6. Atualização do relatório permanece operacional
    update_payload = {
        "projeto": "2",
        "periodo": "5",
        "ent1_conc": "0",
        "ent1_txt": "Entrega 1 P3 realizada - Atualização permitida em bi fechado",
        "ent2_conc": "0",
        "ent2_txt": "Entrega 2 P3 também concluída",
    }
    resp_update = client.post("/api/v1/entregas-jornada/formulario", json=update_payload, headers=admin_headers)
    assert resp_update.status_code == 200

    # 7. Exclusão do relatório permanece operacional
    resp_delete = client.delete(f"/api/v1/entregas-jornada/formularios/{created_id}", headers=admin_headers)
    assert resp_delete.status_code == 200

    # 8. Após exclusão, nova tentativa de preenchimento deve ser bloqueada pois o período continua inativo
    resp_blocked_after_delete = client.post("/api/v1/entregas-jornada/formulario", json=payload, headers=admin_headers)
    assert resp_blocked_after_delete.status_code == 400
    assert "fechado para novos preenchimentos" in resp_blocked_after_delete.json()["detail"]

    # 9. Limpeza: reativa o período 5
    client.put("/api/admin/bimestres-config/5", json={"ativo": True}, headers=admin_headers)
