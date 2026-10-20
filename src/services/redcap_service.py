"""
Serviço de Integração e Processamento Analítico do REDCap
===========================================================
Consome os registros dos 5 projetos da II Jornada de Gestão via API REDCap,
aplica cache em memória com TTL e calcula métricas executivas de entregas.
"""

import time
import logging
from typing import List, Dict, Any, Optional
import httpx
from src.config import settings, PROJECTS, PERIODS, DELIVERIES, PROJ_SUFFIX

logger = logging.getLogger("redcap_service")

# Cache em memória
_CACHE: Dict[str, Any] = {
    "data": [],
    "last_fetched": 0.0,
}


async def fetch_redcap_data(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Busca registros brutos da API REDCap com cache em memória."""
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
                logger.info(f"Dados do REDCap atualizados com sucesso ({len(data)} registros brutos).")
                return data
            else:
                logger.warning(f"Resposta inesperada do REDCap: {data}")
                return _CACHE["data"]
    except Exception as exc:
        logger.error(f"Erro ao consultar API do REDCap: {exc}")
        if _CACHE["data"]:
            logger.warning("Retornando dados em cache anterior devido à falha de conexão.")
            return _CACHE["data"]
        raise


def process_records(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filtra apenas formulários com status 'Complete' (form_1_complete == '2')."""
    if not raw_records:
        return []

    processed = []
    for rec in raw_records:
        # Apenas formulários preenchidos e finalizados no REDCap
        if str(rec.get("form_1_complete", "")) != "2":
            continue

        item: Dict[str, Any] = {
            "record_id": rec.get("record_id"),
            "projeto": str(rec.get("projeto", "")),
            "periodo": str(rec.get("periodo", "")),
            "var_projeto": rec.get("var_projeto"),
            "var_periodo": rec.get("var_periodo"),
            "form_1_complete": rec.get("form_1_complete"),
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
        if period_code is not None:
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
    if period_code is not None:
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
            "periodo_code": p_code,
            "periodo_label": period_label,
            "ent1_txt": r.get(t1_field) or "—",
            "ent2_txt": r.get(t2_field) or "—",
            "ent1_conc": c1_val,
            "ent2_conc": c2_val,
            "ent1_status": "Concluída" if c1_val == "0" else ("Em andamento" if c1_val == "1" else "Não informado"),
            "ent2_status": "Concluída" if c2_val == "0" else ("Em andamento" if c2_val == "1" else "Não informado"),
        })

    bimonthly = get_bimonthly_status(records, proj_key=proj_key)

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
        "bimonthly": bimonthly,
        "timeline": timeline,
    }


async def get_full_dashboard(period_code: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Any]:
    """Retorna todo o payload consolidado do dashboard corporativo."""
    raw = await fetch_redcap_data(force_refresh=force_refresh)
    records = process_records(raw)

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