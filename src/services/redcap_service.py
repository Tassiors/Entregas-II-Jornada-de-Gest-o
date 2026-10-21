"""
Serviço de Integração e Processamento Analítico de Entregas da II Jornada
========================================================================
Consome dados semente da API REDCap em modo ESTRITAMENTE LEITURA (read-only),
persiste e gerencia respostas locais no SQLite corporativo (data/app.db) com
efeito cascata em conclusões/cancelamentos de entregas, cache em memória e métricas executivas.
"""

import time
import logging
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.config import settings, PROJECTS, PERIODS, DELIVERIES, PROJ_SUFFIX
from src.models.formulario_resposta import FormularioResposta

logger = logging.getLogger("redcap_service")

# Cache em memória
_CACHE: Dict[str, Any] = {
    "data": [],
    "last_fetched": 0.0,
}


async def fetch_redcap_data(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Busca registros brutos da API REDCap com cache em memória.
    Modo estritamente LEITURA (action: export). Nenhuma escrita é feita no REDCap.
    """
    global _CACHE
    now = time.time()
    cache_ttl = settings.REDCAP_CACHE_TTL_SECONDS

    if not force_refresh and _CACHE["data"] and (now - _CACHE["last_fetched"] < cache_ttl):
        logger.info("Utilizando dados do REDCap a partir do cache em memória.")
        return _CACHE["data"]

    payload = {
        "token": settings.REDCAP_TOKEN,
        "content": "record",
        "action": "export",
        "format": "json",
        "type": "flat",
        "csvDelimiter": "",
        "rawOrLabel": "raw",
        "rawOrLabelHeaders": "raw",
        "exportCheckboxLabel": "false",
        "exportSurveyFields": "false",
        "exportDataAccessGroups": "false",
        "returnFormat": "json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(settings.REDCAP_API_URL, data=payload)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                _CACHE["data"] = data
                _CACHE["last_fetched"] = now
                logger.info(f"Dados do REDCap lidos com sucesso ({len(data)} registros brutos).")
                return data
            else:
                logger.warning(f"Resposta inesperada do REDCap: {data}")
                return _CACHE["data"]
    except Exception as exc:
        logger.error(f"Erro ao consultar API do REDCap (Read-Only): {exc}")
        if _CACHE["data"]:
            logger.warning("Retornando dados em cache anterior devido à falha de conexão com REDCap.")
            return _CACHE["data"]
        # Se não há conexão e nem cache, retorna lista vazia para operar offline com banco local
        return []


def process_records(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filtra apenas formulários com status 'Complete' (form_1_complete == '2')."""
    if not raw_records:
        return []

    processed = []
    for rec in raw_records:
        if str(rec.get("form_1_complete", "")) != "2":
            continue

        item: Dict[str, Any] = {
            "record_id": str(rec.get("record_id", "")),
            "projeto": str(rec.get("projeto", "")),
            "periodo": str(rec.get("periodo", "")),
            "var_projeto": rec.get("var_projeto"),
            "var_periodo": rec.get("var_periodo"),
            "form_1_complete": rec.get("form_1_complete"),
            "origem": rec.get("origem", "redcap"),
        }

        try:
            item["periodo_num"] = int(rec.get("periodo", 99))
        except (ValueError, TypeError):
            item["periodo_num"] = 99

        for suffix in PROJ_SUFFIX.values():
            for field in [f"ent1_p{suffix}_txt", f"ent2_p{suffix}_txt", f"ent1_p{suffix}_conc", f"ent2_p{suffix}_conc"]:
                if field in rec:
                    item[field] = rec.get(field)

        processed.append(item)

    return processed


async def get_all_merged_records(
    db: Optional[AsyncSession] = None,
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    """
    Mescla os dados semente do REDCap (read-only) com os formulários respondidos
    localmente no SQLite (formulario_respostas).
    Registros locais sobrepõem o REDCap para o mesmo (projeto, periodo).
    Aplica a regra de efeito cascata na visualização analítica.
    """
    raw_redcap = await fetch_redcap_data(force_refresh=force_refresh)
    records = process_records(raw_redcap)

    # Dicionário de registros mapeados por (projeto, periodo)
    merged_map: Dict[str, Dict[str, Any]] = {}
    for r in records:
        key = f"{r.get('projeto')}_{r.get('periodo')}"
        merged_map[key] = r

    # Sobrepõe com registros locais gravados no SQLite
    if db is not None:
        try:
            stmt = select(FormularioResposta).order_by(FormularioResposta.projeto, FormularioResposta.periodo)
            result = await db.execute(stmt)
            local_forms = result.scalars().all()

            for lf in local_forms:
                suffix = PROJ_SUFFIX.get(lf.projeto, "1")
                key = f"{lf.projeto}_{lf.periodo}"
                merged_map[key] = {
                    "id": lf.id,
                    "record_id": str(lf.id),
                    "projeto": lf.projeto,
                    "periodo": lf.periodo,
                    "var_projeto": lf.var_projeto or PROJECTS.get(lf.projeto, {}).get("name", ""),
                    "var_periodo": lf.var_periodo or PERIODS.get(lf.periodo, ""),
                    "form_1_complete": lf.form_1_complete,
                    "origem": "local",
                    "periodo_num": int(lf.periodo) if lf.periodo.isdigit() else 99,
                    f"ent1_p{suffix}_conc": lf.ent1_conc,
                    f"ent1_p{suffix}_txt": lf.ent1_txt,
                    f"ent2_p{suffix}_conc": lf.ent2_conc,
                    f"ent2_p{suffix}_txt": lf.ent2_txt,
                    "usuario_registro": lf.usuario_registro,
                    "updated_at": lf.updated_at.isoformat() if lf.updated_at else None,
                }
        except Exception as exc:
            logger.error(f"Erro ao carregar registros locais de formulario_respostas: {exc}")

    # Lista final consolidada
    final_list = list(merged_map.values())

    # Aplicação de efeito cascata na matriz consolidada para bimestres subsequentes:
    # Para cada projeto, se a entrega foi concluída no bimestre k, ela permanece
    # concluída nos bimestres seguintes k+1..5 (a menos que haja cancelamento explícito).
    for proj_key in PROJECTS.keys():
        suffix = PROJ_SUFFIX.get(proj_key, "1")
        c1_field = f"ent1_p{suffix}_conc"
        c2_field = f"ent2_p{suffix}_conc"

        e1_concluida = False
        e2_concluida = False

        for p_idx in range(6):
            p_code = str(p_idx)
            key = f"{proj_key}_{p_code}"
            if key in merged_map:
                item = merged_map[key]
                v1 = str(item.get(c1_field, "")).strip()
                v2 = str(item.get(c2_field, "")).strip()

                if v1 == "0":
                    e1_concluida = True
                elif v1 == "1":
                    e1_concluida = False
                elif e1_concluida:
                    item[c1_field] = "0"

                if v2 == "0":
                    e2_concluida = True
                elif v2 == "1":
                    e2_concluida = False
                elif e2_concluida:
                    item[c2_field] = "0"

    return final_list


def get_project_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula estatísticas agregadas de conclusão em todos os projetos."""
    total_deliveries = 0
    completed = 0

    for proj_key, suffix in PROJ_SUFFIX.items():
        proj_records = [r for r in records if r.get("projeto") == proj_key]
        for col in [f"ent1_p{suffix}_conc", f"ent2_p{suffix}_conc"]:
            for r in proj_records:
                val = r.get(col)
                if val is not None and str(val).strip() != "":
                    total_deliveries += 1
                    if str(val).strip() == "0":
                        completed += 1

    pct = round((completed / total_deliveries * 100), 1) if total_deliveries > 0 else 0.0
    return {
        "total_deliveries": total_deliveries,
        "completed": completed,
        "completion_rate": pct,
    }


def get_bimonthly_status(records: List[Dict[str, Any]], proj_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retorna o status de entregas para os 6 bimestres."""
    short_names = {
        "0": "Jul/Ago 26",
        "1": "Set/Out 26",
        "2": "Nov/Dez 26",
        "3": "Jan/Fev 27",
        "4": "Mar/Abr 27",
        "5": "Mai/Jun 27",
    }
    target = records
    if proj_key is not None:
        target = [r for r in records if str(r.get("projeto")) == str(proj_key)]

    status_list = []
    for idx, (p_code, p_label) in enumerate(PERIODS.items(), start=1):
        matching = [r for r in target if str(r.get("periodo")) == str(p_code)]
        count = len(matching)
        status_list.append({
            "code": p_code,
            "num_label": f"B{idx}",
            "period_label": p_label,
            "short_name": short_names.get(p_code, f"B{idx}"),
            "entregue": count > 0,
            "count": count,
        })
    return status_list


def get_project_deliveries_matrix(records: List[Dict[str, Any]], period_code: Optional[str] = None) -> List[Dict[str, Any]]:
    """Gera a matriz de status de conclusão das entregas E1 e E2 para os 5 projetos."""
    matrix = []
    for proj_key, p_info in PROJECTS.items():
        suffix = PROJ_SUFFIX.get(proj_key, "1")
        ent1_desc = DELIVERIES.get(proj_key, {}).get("ent1", "Entrega 1")
        ent2_desc = DELIVERIES.get(proj_key, {}).get("ent2", "Entrega 2")

        proj_records = [r for r in records if str(r.get("projeto")) == str(proj_key)]
        if period_code is not None and str(period_code).strip() not in ("", "all", "None"):
            proj_records = [r for r in proj_records if str(r.get("periodo")) == str(period_code)]

        c1_col = f"ent1_p{suffix}_conc"
        c2_col = f"ent2_p{suffix}_conc"

        e1_done = any(str(r.get(c1_col, "")).strip() == "0" for r in proj_records)
        e2_done = any(str(r.get(c2_col, "")).strip() == "0" for r in proj_records)

        matrix.append({
            "proj_key": proj_key,
            "code": p_info["code"],
            "short": p_info["short"],
            "name": p_info["name"],
            "color": p_info["color"],
            "color2": p_info["color2"],
            "icon": p_info["icon"],
            "ent1_desc": ent1_desc,
            "ent2_desc": ent2_desc,
            "e1_done": e1_done,
            "e2_done": e2_done,
        })
    return matrix


def get_project_details(records: List[Dict[str, Any]], proj_key: str, period_code: Optional[str] = None) -> Dict[str, Any]:
    """Retorna o detalhamento com a timeline e textos de evolução de um projeto."""
    p_info = PROJECTS.get(proj_key, {})
    suffix = PROJ_SUFFIX.get(proj_key, "1")
    ent1_desc = DELIVERIES.get(proj_key, {}).get("ent1", "Entrega 1")
    ent2_desc = DELIVERIES.get(proj_key, {}).get("ent2", "Entrega 2")

    proj_records = [r for r in records if str(r.get("projeto")) == str(proj_key)]
    if period_code is not None and str(period_code).strip() not in ("", "all", "None"):
        proj_records = [r for r in proj_records if str(r.get("periodo")) == str(period_code)]

    proj_records.sort(key=lambda r: r.get("periodo_num", 99))

    timeline = []
    t1_field = f"ent1_p{suffix}_txt"
    t2_field = f"ent2_p{suffix}_txt"
    c1_field = f"ent1_p{suffix}_conc"
    c2_field = f"ent2_p{suffix}_conc"

    for r in proj_records:
        p_code = str(r.get("periodo", ""))
        period_label = PERIODS.get(p_code, "—")
        c1_val = str(r.get(c1_field, "")).strip()
        c2_val = str(r.get(c2_field, "")).strip()

        timeline.append({
            "id": r.get("id"),
            "record_id": r.get("record_id"),
            "origem": r.get("origem", "redcap"),
            "periodo_code": p_code,
            "periodo_label": period_label,
            "ent1_txt": r.get(t1_field) or "—",
            "ent2_txt": r.get(t2_field) or "—",
            "ent1_conc": c1_val,
            "ent2_conc": c2_val,
            "ent1_status": "Concluída" if c1_val == "0" else ("Em andamento" if c1_val == "1" else "Não informado"),
            "ent2_status": "Concluída" if c2_val == "0" else ("Em andamento" if c2_val == "1" else "Não informado"),
            "usuario_registro": r.get("usuario_registro"),
            "updated_at": r.get("updated_at"),
        })

    bimonthly = get_bimonthly_status(records, proj_key=proj_key)

    e1_done = any(item.get("ent1_conc") == "0" for item in timeline)
    e2_done = any(item.get("ent2_conc") == "0" for item in timeline)

    return {
        "proj_key": proj_key,
        "code": p_info.get("code", f"P{proj_key}"),
        "short": p_info.get("short", ""),
        "name": p_info.get("name", ""),
        "color": p_info.get("color", "#1565C0"),
        "color2": p_info.get("color2", "#0288D1"),
        "icon": p_info.get("icon", "📋"),
        "ent1_desc": ent1_desc,
        "ent2_desc": ent2_desc,
        "e1_done": e1_done,
        "e2_done": e2_done,
        "bimonthly": bimonthly,
        "timeline": timeline,
    }


async def get_full_dashboard(
    db: Optional[AsyncSession] = None,
    period_code: Optional[str] = None,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """Retorna o payload consolidado do dashboard executivo mesclando REDCap e banco local."""
    records = await get_all_merged_records(db=db, force_refresh=force_refresh)

    summary = get_project_summary(records)
    matrix = get_project_deliveries_matrix(records, period_code=period_code)
    bimonthly_geral = get_bimonthly_status(records)

    projects_detail = {}
    for proj_key in PROJECTS.keys():
        projects_detail[proj_key] = get_project_details(records, proj_key, period_code=period_code)

    return {
        "summary": summary,
        "matrix": matrix,
        "bimonthly_geral": bimonthly_geral,
        "projects_detail": projects_detail,
        "periods": PERIODS,
        "selected_period": period_code,
        "last_sync": time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(_CACHE["last_fetched"] or time.time())),
    }


def clear_cache():
    """Invalida o cache local."""
    global _CACHE
    _CACHE["data"] = []
    _CACHE["last_fetched"] = 0.0


def get_form_schema() -> Dict[str, Any]:
    """Retorna os metadados e estrutura oficial do formulário da II Jornada de Gestão."""
    form_projects = {}
    for code, p in PROJECTS.items():
        suffix = PROJ_SUFFIX.get(code, "1")
        form_projects[code] = {
            "code": p["code"],
            "short": p["short"],
            "name": p["name"],
            "color": p["color"],
            "color2": p["color2"],
            "icon": p["icon"],
            "ent1_desc": DELIVERIES.get(code, {}).get("ent1", ""),
            "ent2_desc": DELIVERIES.get(code, {}).get("ent2", ""),
            "field_ent1_conc": f"ent1_p{suffix}_conc",
            "field_ent1_txt": f"ent1_p{suffix}_txt",
            "field_ent2_conc": f"ent2_p{suffix}_conc",
            "field_ent2_txt": f"ent2_p{suffix}_txt",
        }

    return {
        "title": "Acompanhamento Entregas II Jornada de Gestão",
        "instructions": (
            "<p>Este formulário foi desenvolvido para apoiar o acompanhamento das entregas definidas durante a "
            "<strong>II Jornada de Gestão do HC-UFPE</strong>, permitindo o registro, o monitoramento e a atualização do andamento das ações pactuadas.</p>"
            "<p>A ferramenta busca facilitar o acompanhamento sistemático das entregas, contribuindo para maior transparência, organização e efetividade na execução das ações previstas.</p>"
        ),
        "acknowledgement": (
            "<p><strong>Agradecimento</strong></p>"
            "<p>Agradecemos a colaboração e o compromisso de todos os envolvidos no acompanhamento das entregas da "
            "<strong>II Jornada de Gestão do HC-UFPE</strong>. A participação de cada gerente é fundamental para fortalecer a gestão, promover o cumprimento das ações pactuadas e contribuir para o alcance dos objetivos institucionais.</p>"
        ),
        "projects": form_projects,
        "periods": PERIODS,
        "conclusion_options": [
            {"value": "0", "label": "Sim", "color": "emerald"},
            {"value": "1", "label": "Não", "color": "slate"},
        ],
    }


async def get_project_cascade_status(
    db: Optional[AsyncSession],
    proj_code: str,
    before_period: int,
) -> Dict[str, Any]:
    """
    Verifica se a Entrega 1 ou a Entrega 2 já foram concluídas em algum bimestre anterior a before_period.
    Retorna o status e o rótulo do período onde a conclusão ocorreu.
    """
    e1_concluida = False
    e1_periodo = None
    e2_concluida = False
    e2_periodo = None

    if before_period <= 0:
        return {
            "e1_concluida": False,
            "e1_periodo": None,
            "e2_concluida": False,
            "e2_periodo": None,
        }

    previous_periods = [str(i) for i in range(before_period)]
    suffix = PROJ_SUFFIX.get(proj_code, "1")

    # 1. Consulta registros locais no SQLite
    if db is not None:
        try:
            stmt = select(FormularioResposta).where(
                FormularioResposta.projeto == proj_code,
                FormularioResposta.periodo.in_(previous_periods),
            ).order_by(FormularioResposta.periodo.asc())
            res = await db.execute(stmt)
            for r in res.scalars().all():
                if str(r.ent1_conc).strip() == "0" and not e1_concluida:
                    e1_concluida = True
                    p_idx = int(r.periodo) + 1 if r.periodo.isdigit() else r.periodo
                    e1_periodo = f"B{p_idx} — {PERIODS.get(r.periodo, '')}"
                if str(r.ent2_conc).strip() == "0" and not e2_concluida:
                    e2_concluida = True
                    p_idx = int(r.periodo) + 1 if r.periodo.isdigit() else r.periodo
                    e2_periodo = f"B{p_idx} — {PERIODS.get(r.periodo, '')}"
        except Exception as exc:
            logger.error(f"Erro ao verificar cascata local: {exc}")

    # 2. Complementa com dados semente do REDCap se ainda não encontrou
    if not (e1_concluida and e2_concluida):
        try:
            raw = await fetch_redcap_data(force_refresh=False)
            c1_col = f"ent1_p{suffix}_conc"
            c2_col = f"ent2_p{suffix}_conc"
            for r in raw:
                p_str = str(r.get("periodo", "")).strip()
                if str(r.get("projeto", "")).strip() == proj_code and p_str in previous_periods:
                    if str(r.get(c1_col, "")).strip() == "0" and not e1_concluida:
                        e1_concluida = True
                        p_idx = int(p_str) + 1 if p_str.isdigit() else p_str
                        e1_periodo = f"B{p_idx} — {PERIODS.get(p_str, '')}"
                    if str(r.get(c2_col, "")).strip() == "0" and not e2_concluida:
                        e2_concluida = True
                        p_idx = int(p_str) + 1 if p_str.isdigit() else p_str
                        e2_periodo = f"B{p_idx} — {PERIODS.get(p_str, '')}"
        except Exception as exc:
            logger.error(f"Erro ao verificar cascata REDCap: {exc}")

    return {
        "e1_concluida": e1_concluida,
        "e1_periodo": e1_periodo,
        "e2_concluida": e2_concluida,
        "e2_periodo": e2_periodo,
    }


async def find_existing_record(
    db: Optional[AsyncSession],
    projeto: str,
    periodo: str
) -> Optional[Dict[str, Any]]:
    """
    Localiza se já existe um registro para o projeto e período especificados.
    Prioriza o banco local SQLite; faz fallback para o cache do REDCap se não houver localmente.
    """
    proj_str = str(projeto).strip()
    period_str = str(periodo).strip()

    # 1. Consulta o banco local
    if db is not None:
        stmt = select(FormularioResposta).where(
            FormularioResposta.projeto == proj_str,
            FormularioResposta.periodo == period_str,
        )
        res = await db.execute(stmt)
        local_rec = res.scalars().first()
        if local_rec:
            return {
                "id": local_rec.id,
                "record_id": str(local_rec.id),
                "projeto": local_rec.projeto,
                "periodo": local_rec.periodo,
                "ent1_conc": local_rec.ent1_conc,
                "ent1_txt": local_rec.ent1_txt,
                "ent2_conc": local_rec.ent2_conc,
                "ent2_txt": local_rec.ent2_txt,
                "form_1_complete": local_rec.form_1_complete,
                "usuario_registro": local_rec.usuario_registro,
                "origem": "local",
                "created_at": local_rec.created_at.isoformat() if local_rec.created_at else None,
                "updated_at": local_rec.updated_at.isoformat() if local_rec.updated_at else None,
            }

    # 2. Fallback: Consulta registros semente do REDCap
    raw = await fetch_redcap_data(force_refresh=False)
    suffix = PROJ_SUFFIX.get(proj_str, "1")

    for r in raw:
        if str(r.get("projeto", "")).strip() == proj_str and str(r.get("periodo", "")).strip() == period_str:
            return {
                "id": None,
                "record_id": str(r.get("record_id", "")),
                "projeto": str(r.get("projeto", "")),
                "periodo": str(r.get("periodo", "")),
                "ent1_conc": str(r.get(f"ent1_p{suffix}_conc", "") or "1"),
                "ent1_txt": str(r.get(f"ent1_p{suffix}_txt", "") or ""),
                "ent2_conc": str(r.get(f"ent2_p{suffix}_conc", "") or "1"),
                "ent2_txt": str(r.get(f"ent2_p{suffix}_txt", "") or ""),
                "form_1_complete": str(r.get("form_1_complete", "2") or "2"),
                "origem": "redcap",
            }
    return None


async def save_local_form_record(
    db: AsyncSession,
    form_data: Dict[str, Any],
    usuario: str = "SISTEMA",
) -> Dict[str, Any]:
    """
    Grava ou atualiza a resposta do formulário exclusivamente no banco de dados local SQLite.
    NÃO realiza chamadas de importação no REDCap (estritamente read-only).
    Aplica a regra de efeito cascata para os bimestres subsequentes do mesmo projeto.
    """
    proj_code = str(form_data.get("projeto", "")).strip()
    period_code = str(form_data.get("periodo", "")).strip()

    if proj_code not in PROJECTS:
        raise ValueError(f"Projeto inválido: {proj_code}")
    if period_code not in PERIODS:
        raise ValueError(f"Período inválido: {period_code}")

    ent1_conc = str(form_data.get("ent1_conc", "1")).strip()
    ent1_txt = str(form_data.get("ent1_txt", "")).strip()
    ent2_conc = str(form_data.get("ent2_conc", "1")).strip()
    ent2_txt = str(form_data.get("ent2_txt", "")).strip()

    # 1. Verifica se já existe registro para este (projeto, período)
    stmt = select(FormularioResposta).where(
        FormularioResposta.projeto == proj_code,
        FormularioResposta.periodo == period_code,
    )
    result = await db.execute(stmt)
    registro = result.scalars().first()

    dados_anteriores = registro.to_dict() if registro else None

    if registro:
        registro.ent1_conc = ent1_conc
        registro.ent1_txt = ent1_txt
        registro.ent2_conc = ent2_conc
        registro.ent2_txt = ent2_txt
        registro.form_1_complete = "2"
        registro.usuario_registro = usuario
    else:
        registro = FormularioResposta(
            projeto=proj_code,
            periodo=period_code,
            var_projeto=PROJECTS[proj_code]["name"],
            var_periodo=PERIODS[period_code],
            ent1_conc=ent1_conc,
            ent1_txt=ent1_txt,
            ent2_conc=ent2_conc,
            ent2_txt=ent2_txt,
            form_1_complete="2",
            usuario_registro=usuario,
        )
        db.add(registro)

    # 2. Efeito cascata para bimestres seguintes (Bk+1 .. 5):
    # Se uma entrega for concluída ("0"), permanece com status concluído nos bimestres subsequentes.
    # Se o usuário cancelar a conclusão ("1"), o cancelamento também se propaga em cascata nos bimestres seguintes.
    try:
        current_period_idx = int(period_code)
    except (ValueError, TypeError):
        current_period_idx = 0

    if current_period_idx < 5:
        # Busca registros dos bimestres seguintes existentes para este projeto
        subsequent_periods = [str(i) for i in range(current_period_idx + 1, 6)]
        stmt_sub = select(FormularioResposta).where(
            FormularioResposta.projeto == proj_code,
            FormularioResposta.periodo.in_(subsequent_periods),
        )
        sub_results = await db.execute(stmt_sub)
        sub_records = sub_results.scalars().all()

        for sub_rec in sub_records:
            # Propagação da Entrega 1
            if ent1_conc == "0":
                sub_rec.ent1_conc = "0"
            elif ent1_conc == "1":
                sub_rec.ent1_conc = "1"

            # Propagação da Entrega 2
            if ent2_conc == "0":
                sub_rec.ent2_conc = "0"
            elif ent2_conc == "1":
                sub_rec.ent2_conc = "1"

    await db.commit()
    await db.refresh(registro)

    clear_cache()

    return {
        "status": "success",
        "id": registro.id,
        "record_id": str(registro.id),
        "projeto": proj_code,
        "periodo": period_code,
        "message": "Formulário de acompanhamento salvo com sucesso no banco de dados local.",
        "dados_anteriores": dados_anteriores,
        "dados_novos": registro.to_dict(),
        "acknowledgement": (
            "Agradecemos a colaboração e o compromisso de todos os envolvidos no acompanhamento das entregas da "
            "II Jornada de Gestão do HC-UFPE. A participação de cada gerente é fundamental para fortalecer a gestão, "
            "promover o cumprimento das ações pactuadas e contribuir para o alcance dos objetivos institucionais."
        )
    }


async def get_local_form_records(
    db: AsyncSession,
    projeto: Optional[str] = None,
    periodo: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lista as respostas de formulários armazenadas no banco local SQLite."""
    stmt = select(FormularioResposta)
    if projeto is not None:
        stmt = stmt.where(FormularioResposta.projeto == str(projeto))
    if periodo is not None:
        stmt = stmt.where(FormularioResposta.periodo == str(periodo))
    stmt = stmt.order_by(FormularioResposta.id.desc())

    res = await db.execute(stmt)
    records = res.scalars().all()
    return [r.to_dict() for r in records]


async def get_local_form_record_by_id(
    db: AsyncSession,
    record_id: int,
) -> Optional[Dict[str, Any]]:
    """Obtém uma resposta de formulário pelo ID."""
    stmt = select(FormularioResposta).where(FormularioResposta.id == record_id)
    res = await db.execute(stmt)
    rec = res.scalars().first()
    return rec.to_dict() if rec else None


async def delete_local_form_record(
    db: AsyncSession,
    record_id: int,
) -> Optional[Dict[str, Any]]:
    """Exclui um formulário respondido no banco local SQLite."""
    stmt = select(FormularioResposta).where(FormularioResposta.id == record_id)
    res = await db.execute(stmt)
    rec = res.scalars().first()
    if not rec:
        return None

    dados_excluidos = rec.to_dict()
    await db.delete(rec)
    await db.commit()
    clear_cache()
    return dados_excluidos