"""
Roteador da API: Acompanhamento de Entregas da II Jornada de Gestão
===================================================================
Endpoints para visualização analítica, matriz de entregas dos 5 projetos,
leitura do REDCap (estritamente read-only) e operações CRUD locais no SQLite
com efeito cascata e controle de acesso RBAC por projeto.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, Path, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.auth.auth import auth_handler
from src.resources.database import get_app_db_session
from src.helpers.audit_helper import registrar_auditoria
from src.models.usuario_sistema import UsuarioSistema
from src.models.formulario_resposta import FormularioResposta
from src.models.configuracao_bimestre import ConfiguracaoBimestre, init_default_bimestres
from src.services.redcap_service import (
    get_full_dashboard,
    fetch_redcap_data,
    process_records,
    get_project_summary,
    get_project_deliveries_matrix,
    get_bimonthly_status,
    get_project_details,
    clear_cache,
    get_form_schema,
    find_existing_record,
    get_project_cascade_status,
    save_local_form_record,
    get_local_form_records,
    get_local_form_record_by_id,
    delete_local_form_record,
)
from src.config import PROJECTS, PERIODS

router = APIRouter(
    prefix="/api/v1/entregas-jornada",
    tags=["II Jornada de Gestão - Entregas"],
)

ADMIN_GROUP = "GLO-SEC-HCPE-SETISD"


class FormularioEntregaSchema(BaseModel):
    record_id: Optional[str] = Field(None, description="ID do registro local (opcional)")
    projeto: str = Field(..., description="Código do projeto (0 a 4)")
    periodo: str = Field(..., description="Código do período bimestral (0 a 5)")
    ent1_conc: str = Field("1", description="Status de conclusão da Entrega 1 ('0' Sim / '1' Não)")
    ent1_txt: Optional[str] = Field("", description="Comentários/Evolução da entrega 1")
    ent2_conc: str = Field("1", description="Status de conclusão da Entrega 2 ('0' Sim / '1' Não)")
    ent2_txt: Optional[str] = Field("", description="Comentários/Evolução da entrega 2")

    @model_validator(mode="after")
    def validate_comentarios_quando_nao_concluida(self):
        # Se a entrega NÃO estiver concluída ("1"), o comentário é obrigatório
        if self.ent1_conc == "1" and not (self.ent1_txt and self.ent1_txt.strip()):
            raise ValueError("O campo 'Comentários / Evolução da Entrega 1' é obrigatório enquanto a entrega não estiver concluída.")
        if self.ent2_conc == "1" and not (self.ent2_txt and self.ent2_txt.strip()):
            raise ValueError("O campo 'Comentários / Evolução da Entrega 2' é obrigatório enquanto a entrega não estiver concluída.")
        return self


async def validar_permissao_projeto(
    projeto_alvo: str,
    current_user: Optional[dict],
    db: AsyncSession,
) -> str:
    """
    Verifica se o usuário tem autorização para criar/atualizar/excluir registros do projeto.
    - Administradores (grupo AD ou perfil ADMINISTRADOR) têm acesso irrestrito.
    - Gerentes de Projeto (GERENTE_PROJETO) só podem agir no seu 'projeto_atribuido'.
    - Demais perfis recebem HTTP 403 Forbidden.
    """
    if not current_user:
        # Se estiver sem autenticação em ambiente de dev ou chamada direta
        return "USUARIO_LOCAL"

    username = current_user.get("username", "")
    groups = current_user.get("groups", [])

    # 1. Verifica se é Administrador pelo grupo AD
    if ADMIN_GROUP in groups or username == "admin":
        return username

    # 2. Busca cadastro do usuário no banco local
    stmt = select(UsuarioSistema).where(
        UsuarioSistema.username == username,
        UsuarioSistema.ativo == True,
    )
    res = await db.execute(stmt)
    user_db = res.scalars().first()

    if not user_db:
        # Usuário não cadastrado localmente no RBAC
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seu usuário não possui perfil de gestão autorizado no sistema local.",
        )

    if user_db.perfil == "ADMINISTRADOR":
        return username

    if user_db.perfil == "GERENTE_PROJETO":
        if str(user_db.projeto_atribuido).strip() != str(projeto_alvo).strip():
            proj_name = PROJECTS.get(str(user_db.projeto_atribuido), {}).get("name", f"Projeto {user_db.projeto_atribuido}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado: Você é gerente apenas do '{proj_name}' e não pode alterar este projeto.",
            )
        return username

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Seu perfil de acesso é apenas de consulta e não tem permissão para realizar alterações.",
    )


# ==============================================================================
# Endpoints de Visualização do Painel (Públicos / Somente Leitura)
# ==============================================================================

@router.get(
    "/dashboard",
    summary="Dashboard consolidado da II Jornada",
    description="Retorna resumo executivo, matriz de entregas dos 5 projetos, status bimestral e detalhes.",
)
async def get_dashboard(
    periodo: Optional[str] = Query(None, description="Código do período bimestral (0 a 5) ou vazio para todos"),
    force_refresh: bool = Query(False, description="Forçar atualização dos dados"),
    db: AsyncSession = Depends(get_app_db_session),
):
    try:
        data = await get_full_dashboard(db=db, period_code=periodo, force_refresh=force_refresh)
        return data
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao gerar dados do painel: {str(exc)}",
        )


@router.get(
    "/summary",
    summary="Resumo de entregas",
    description="Retorna total de entregas cadastradas, quantidade de concluídas e taxa percentual.",
)
async def get_summary(
    force_refresh: bool = Query(False, description="Forçar atualização dos dados"),
    db: AsyncSession = Depends(get_app_db_session),
):
    try:
        dashboard = await get_full_dashboard(db=db, force_refresh=force_refresh)
        return dashboard["summary"]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter resumo: {str(exc)}",
        )


@router.get(
    "/matrix",
    summary="Matriz de entregas dos 5 projetos",
    description="Retorna o status de conclusão de E1 e E2 para cada projeto.",
)
async def get_matrix(
    periodo: Optional[str] = Query(None, description="Código do período bimestral"),
    force_refresh: bool = Query(False, description="Forçar atualização dos dados"),
    db: AsyncSession = Depends(get_app_db_session),
):
    try:
        dashboard = await get_full_dashboard(db=db, period_code=periodo, force_refresh=force_refresh)
        return dashboard["matrix"]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    db: AsyncSession = Depends(get_app_db_session),
):
    try:
        dashboard = await get_full_dashboard(db=db, force_refresh=force_refresh)
        return dashboard["bimonthly_geral"]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter bimestres: {str(exc)}",
        )


@router.get(
    "/bimestres-status",
    summary="Status de disponibilidade dos bimestres para preenchimento",
    description="Retorna o status de abertura dos bimestres e se o projeto possui relatório já submetido.",
)
async def get_bimestres_status(
    projeto: Optional[str] = Query(None, description="Código do projeto (0 a 4)"),
    db: AsyncSession = Depends(get_app_db_session),
    current_user: Optional[dict] = Depends(auth_handler.decode_token_optional),
):
    await init_default_bimestres(db)
    stmt = select(ConfiguracaoBimestre).order_by(ConfiguracaoBimestre.periodo_code.asc())
    res = await db.execute(stmt)
    bimestres = res.scalars().all()

    existing_periods = set()
    if projeto:
        stmt_rec = select(FormularioResposta.periodo).where(FormularioResposta.projeto == str(projeto).strip())
        res_rec = await db.execute(stmt_rec)
        for p in res_rec.scalars().all():
            existing_periods.add(str(p).strip())

    result = {}
    for b in bimestres:
        has_sub = str(b.periodo_code) in existing_periods
        result[b.periodo_code] = {
            "periodo_code": b.periodo_code,
            "periodo_nome": b.periodo_nome,
            "ativo": b.ativo,
            "has_submission": has_sub,
            "can_fill": b.ativo or has_sub,
        }
    return result


@router.get(
    "/projetos/{proj_key}",
    summary="Detalhamento de um projeto",
    description="Retorna timeline, status das entregas e evolução bimestral do projeto.",
)
async def get_projeto(
    proj_key: str = Path(..., description="Código do projeto (0 a 4)"),
    periodo: Optional[str] = Query(None, description="Código do período bimestral"),
    force_refresh: bool = Query(False, description="Forçar atualização dos dados"),
    db: AsyncSession = Depends(get_app_db_session),
):
    if proj_key not in PROJECTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projeto '{proj_key}' não encontrado. Opções válidas: {list(PROJECTS.keys())}",
        )
    try:
        dashboard = await get_full_dashboard(db=db, period_code=periodo, force_refresh=force_refresh)
        proj_detail = dashboard["projects_detail"].get(proj_key)
        if not proj_detail:
            raise HTTPException(status_code=404, detail="Detalhes do projeto não localizados")
        return proj_detail
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter detalhes do projeto: {str(exc)}",
        )


@router.post(
    "/sync",
    summary="Sincronizar cache do sistema",
    description="Invalida o cache e força nova coleta de dados semente no REDCap.",
)
async def sync_redcap(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: Optional[dict] = Depends(auth_handler.decode_token_optional),
):
    try:
        clear_cache()
        data = await get_full_dashboard(db=db, force_refresh=True)
        return {
            "status": "success",
            "message": "Dados sincronizados com sucesso.",
            "total_records": len(data.get("matrix", [])),
            "last_sync": data.get("last_sync"),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao sincronizar dados: {str(exc)}",
        )


@router.get(
    "/form-schema",
    summary="Estrutura e metadados do Formulário de Acompanhamento",
    description="Retorna metadados oficiais, textos institucionais e relação de projetos.",
)
async def get_form_metadata():
    try:
        return get_form_schema()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter esquema do formulário: {str(exc)}",
        )


@router.get(
    "/registro-existente",
    summary="Buscar registro existente de um projeto no período",
    description="Verifica se já há um registro preenchido no banco local ou no REDCap e calcula herança cascata.",
)
async def get_existing_form_record(
    projeto: str = Query(..., description="Código do projeto (0 a 4)"),
    periodo: str = Query(..., description="Código do período (0 a 5)"),
    db: AsyncSession = Depends(get_app_db_session),
):
    try:
        existing = await find_existing_record(db=db, projeto=projeto, periodo=periodo)

        try:
            curr_p = int(periodo)
        except (ValueError, TypeError):
            curr_p = 0

        cascade_info = await get_project_cascade_status(db=db, proj_code=projeto, before_period=curr_p)

        # Se não há registro gravado para o período atual, monta sugestão herdada do efeito cascata
        if existing is None and (cascade_info["e1_concluida"] or cascade_info["e2_concluida"]):
            suggested = {
                "id": None,
                "record_id": None,
                "projeto": projeto,
                "periodo": periodo,
                "ent1_conc": "0" if cascade_info["e1_concluida"] else "1",
                "ent1_txt": "",
                "ent2_conc": "0" if cascade_info["e2_concluida"] else "1",
                "ent2_txt": "",
                "form_1_complete": "2",
                "origem": "cascata_sugerida",
            }
            return {
                "exists": False,
                "record": suggested,
                "cascade_info": cascade_info,
            }

        return {
            "exists": existing is not None,
            "record": existing,
            "cascade_info": cascade_info,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar registro existente: {str(exc)}",
        )


# ==============================================================================
# Endpoints de CRUD Local de Formulários (Persistência no SQLite + RBAC)
# ==============================================================================

@router.get(
    "/formularios",
    summary="Listar formulários respondidos localmente",
    description="Retorna os registros de formulários gravados no banco local SQLite.",
)
async def list_formularios(
    projeto: Optional[str] = Query(None, description="Filtrar por código de projeto"),
    periodo: Optional[str] = Query(None, description="Filtrar por período"),
    db: AsyncSession = Depends(get_app_db_session),
    current_user: Optional[dict] = Depends(auth_handler.decode_token_optional),
):
    try:
        records = await get_local_form_records(db=db, projeto=projeto, periodo=periodo)
        return records
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar formulários: {str(exc)}",
        )


@router.get(
    "/formularios/{id}",
    summary="Obter formulário por ID",
    description="Retorna o formulário gravado localmente pelo seu identificador primário.",
)
async def get_formulario_by_id(
    id: int = Path(..., description="ID do formulário"),
    db: AsyncSession = Depends(get_app_db_session),
    current_user: Optional[dict] = Depends(auth_handler.decode_token_optional),
):
    rec = await get_local_form_record_by_id(db=db, record_id=id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formulário não encontrado.")
    return rec


@router.post(
    "/formulario",
    summary="Submeter ou atualizar formulário de entrega",
    description="Grava a resposta no SQLite local, propaga efeito cascata para bimestres posteriores e audita a ação.",
)
async def submit_form(
    payload: FormularioEntregaSchema,
    request: Request,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: Optional[dict] = Depends(auth_handler.decode_token_optional),
):
    # 1. Validação de RBAC do Gerente de Projeto / Administrador
    usuario_audit = await validar_permissao_projeto(payload.projeto, current_user, db)

    # 1.1 Verificação de Disponibilidade do Bimestre para Novos Preenchimentos
    # Se o registro já existir, trata-se de atualização (permitida mesmo se o bimestre estiver inativo).
    # Se não existir e o bimestre estiver desabilitado, rejeita com HTTP 400.
    existing_rec = await find_existing_record(db=db, projeto=payload.projeto, periodo=payload.periodo)
    stmt_bimestre = select(ConfiguracaoBimestre).where(ConfiguracaoBimestre.periodo_code == payload.periodo)
    res_b = await db.execute(stmt_bimestre)
    b_cfg = res_b.scalars().first()
    if b_cfg and not b_cfg.ativo:
        if not existing_rec:
            periodo_nome = PERIODS.get(payload.periodo, f"Bimestre {payload.periodo}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O {periodo_nome} está fechado para novos preenchimentos pelo administrador.",
            )

    try:
        # 2. Grava no banco local SQLite com efeito cascata (SEM gravar no REDCap)
        result = await save_local_form_record(
            db=db,
            form_data=payload.model_dump(),
            usuario=usuario_audit,
        )

        # 3. Registra auditoria corporativa
        client_ip = request.client.host if request.client else "127.0.0.1"
        await registrar_auditoria(
            db=db,
            usuario=usuario_audit,
            categoria="NEGOCIO_CLINICO",
            acao="SALVAR_ENTREGA_JORNADA",
            recurso=f"projeto:{payload.projeto}:periodo:{payload.periodo}:id:{result.get('id')}",
            dados_anteriores=result.get("dados_anteriores"),
            dados_novos=result.get("dados_novos"),
            ip_origem=client_ip,
        )

        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar formulário no banco local: {str(exc)}",
        )


@router.put(
    "/formularios/{id}",
    summary="Atualizar formulário de entrega por ID",
    description="Atualiza um formulário existente no banco local, propaga efeito cascata e audita a alteração.",
)
async def update_form(
    payload: FormularioEntregaSchema,
    request: Request,
    id: int = Path(..., description="ID do formulário"),
    db: AsyncSession = Depends(get_app_db_session),
    current_user: Optional[dict] = Depends(auth_handler.decode_token_optional),
):
    # 1. Validação de RBAC
    usuario_audit = await validar_permissao_projeto(payload.projeto, current_user, db)

    existing = await get_local_form_record_by_id(db=db, record_id=id)
    if not existing:
        existing = await find_existing_record(db=db, projeto=payload.projeto, periodo=payload.periodo)

    try:
        result = await save_local_form_record(
            db=db,
            form_data=payload.model_dump(),
            usuario=usuario_audit,
        )

        client_ip = request.client.host if request.client else "127.0.0.1"
        await registrar_auditoria(
            db=db,
            usuario=usuario_audit,
            categoria="NEGOCIO_CLINICO",
            acao="ATUALIZAR_ENTREGA_JORNADA",
            recurso=f"projeto:{payload.projeto}:periodo:{payload.periodo}:id:{id}",
            dados_anteriores=existing,
            dados_novos=result.get("dados_novos"),
            ip_origem=client_ip,
        )

        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar formulário: {str(exc)}",
        )


@router.delete(
    "/formularios/{id}",
    summary="Excluir formulário de entrega",
    description="Exclui a resposta de formulário do banco local e audita a operação.",
)
async def delete_form(
    request: Request,
    id: int = Path(..., description="ID do formulário"),
    db: AsyncSession = Depends(get_app_db_session),
    current_user: Optional[dict] = Depends(auth_handler.decode_token_optional),
):
    existing = await get_local_form_record_by_id(db=db, record_id=id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formulário não encontrado para exclusão.")

    # Validação de RBAC com base no projeto do registro
    usuario_audit = await validar_permissao_projeto(existing["projeto"], current_user, db)

    try:
        dados_excluidos = await delete_local_form_record(db=db, record_id=id)

        client_ip = request.client.host if request.client else "127.0.0.1"
        await registrar_auditoria(
            db=db,
            usuario=usuario_audit,
            categoria="NEGOCIO_CLINICO",
            acao="EXCLUIR_ENTREGA_JORNADA",
            recurso=f"projeto:{existing['projeto']}:periodo:{existing['periodo']}:id:{id}",
            dados_anteriores=dados_excluidos,
            dados_novos=None,
            ip_origem=client_ip,
        )

        return {
            "status": "success",
            "message": f"Formulário #{id} excluído com sucesso do banco local.",
            "deleted_record": dados_excluidos,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir formulário: {str(exc)}",
        )