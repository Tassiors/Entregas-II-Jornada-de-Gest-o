"""
Roteador da API: Acompanhamento de Entregas da II Jornada de Gestão
===================================================================
Endpoints para visualização executiva, matriz de projetos, bimestres e
sincronização em tempo real com o REDCap.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from src.services.redcap_service import (
    get_full_dashboard,
    fetch_redcap_data,
    process_records,
    get_project_summary,
    get_project_deliveries_matrix,
    get_bimonthly_status,
    get_project_details,
    clear_cache,
)
from src.config import PROJECTS, PERIODS

router = APIRouter(
    prefix="/api/v1/entregas-jornada",
    tags=["II Jornada de Gestão - Entregas"],
)


@router.get(
    "/dashboard",
    summary="Dashboard consolidado da II Jornada",
    description="Retorna resumo executivo, matriz de entregas dos 5 projetos, status bimestral e detalhes.",
)
async def get_dashboard(
    periodo: Optional[str] = Query(None, description="Código do período bimestral (0 a 5) ou vazio para todos"),
    force_refresh: bool = Query(False, description="Forçar busca de dados atualizados na API do REDCap"),
):
    try:
        data = await get_full_dashboard(period_code=periodo, force_refresh=force_refresh)
        return data
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha na comunicação ou processamento do REDCap: {str(exc)}",
        )


@router.get(
    "/summary",
    summary="Resumo de entregas",
    description="Retorna total de entregas cadastradas, quantidade de concluídas e taxa percentual.",
)
async def get_summary(
    force_refresh: bool = Query(False, description="Forçar atualização dos dados"),
):
    try:
        raw = await fetch_redcap_data(force_refresh=force_refresh)
        records = process_records(raw)
        return get_project_summary(records)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao obter resumo do REDCap: {str(exc)}",
        )


@router.get(
    "/matrix",
    summary="Matriz de entregas dos 5 projetos",
    description="Retorna o status de conclusão de E1 e E2 para cada projeto.",
)
async def get_matrix(
    periodo: Optional[str] = Query(None, description="Código do período bimestral"),
    force_refresh: bool = Query(False, description="Forçar atualização dos dados"),
):
    try:
        raw = await fetch_redcap_data(force_refresh=force_refresh)
        records = process_records(raw)
        return get_project_deliveries_matrix(records, period_code=periodo)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao obter matriz de entregas: {str(exc)}",
        )


@router.get(
    "/bimestres",
    summary="Status dos 6 bimestres",
    description="Retorna a relação dos 6 bimestres com contagem de entregas cadastradas.",
)
async def get_bimestres(
    projeto: Optional[str] = Query(None, description="Filtrar por código de projeto específico (0 a 4)"),
    force_refresh: bool = Query(False, description="Forçar atualização dos dados"),
):
    try:
        raw = await fetch_redcap_data(force_refresh=force_refresh)
        records = process_records(raw)
        return get_bimonthly_status(records, proj_key=projeto)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao obter bimestres: {str(exc)}",
        )


@router.get(
    "/projetos/{proj_key}",
    summary="Detalhamento de um projeto",
    description="Retorna timeline, status das entregas e evolução bimestral do projeto.",
)
async def get_projeto(
    proj_key: str,
    periodo: Optional[str] = Query(None, description="Código do período bimestral"),
    force_refresh: bool = Query(False, description="Forçar atualização dos dados"),
):
    if proj_key not in PROJECTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projeto '{proj_key}' não encontrado. Opções válidas: {list(PROJECTS.keys())}",
        )
    try:
        raw = await fetch_redcap_data(force_refresh=force_refresh)
        records = process_records(raw)
        return get_project_details(records, proj_key=proj_key, period_code=periodo)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao obter detalhes do projeto: {str(exc)}",
        )


@router.post(
    "/sync",
    summary="Sincronizar dados com o REDCap",
    description="Invalida o cache e força nova coleta de dados na API oficial.",
)
async def sync_redcap():
    try:
        clear_cache()
        data = await get_full_dashboard(force_refresh=True)
        return {
            "status": "success",
            "message": "Dados sincronizados com sucesso com o REDCap.",
            "total_records": len(data.get("matrix", [])),
            "last_sync": data.get("last_sync"),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha ao sincronizar com o REDCap: {str(exc)}",
        )