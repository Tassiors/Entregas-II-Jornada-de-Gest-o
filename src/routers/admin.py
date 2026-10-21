from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..models.usuario_sistema import UsuarioSistema
from ..models.configuracao_bimestre import ConfiguracaoBimestre, init_default_bimestres
from ..helpers.audit_helper import registrar_auditoria
from ..config import PROJECTS

router = APIRouter(prefix="/api", tags=["Admin"])

ADMIN_GROUP = "GLO-SEC-HCPE-SETISD"


async def verify_admin_group(current_user: dict = Depends(auth_handler.decode_token)):
    username = current_user.get("username", "")
    groups = current_user.get("groups", [])
    if ADMIN_GROUP not in groups and username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito: Privilégios de Administrador são obrigatórios.",
        )
    return current_user


class AdminData(BaseModel):
    message: str
    user_groups: List[str]


@router.get("/admin-only-data", response_model=AdminData)
async def get_admin_data(current_user: dict = Depends(verify_admin_group)):
    return AdminData(
        message="This is highly confidential admin data!",
        user_groups=current_user.get("groups", [])
    )


class ADUserSearchResponse(BaseModel):
    exists: bool
    username: str
    displayName: str
    email: str
    department: str


@router.get("/admin/ad-user-search/{username}", response_model=ADUserSearchResponse)
async def search_ad_user(username: str, current_user: dict = Depends(verify_admin_group)):
    """
    Busca e valida um usuário no Active Directory (ou Mock) pelo login de rede.
    Restrito a administradores do sistema.
    """
    res = auth_handler.search_ad_user(username)
    return ADUserSearchResponse(**res)


class UsuarioCreateSchema(BaseModel):
    username: str = Field(..., min_length=2, description="Login de rede corporativo (AD)")
    nome: str = Field(..., min_length=2, description="Nome completo do colaborador")
    email: Optional[str] = Field(None, description="E-mail corporativo")
    departamento: Optional[str] = Field(None, description="Setor ou unidade hospitalar")
    perfil: str = Field(..., description="Perfil de acesso (ex: ADMINISTRADOR, GERENTE_PROJETO, CONSULTA)")
    projeto_atribuido: Optional[str] = Field(None, description="Código do projeto atribuído (0 a 4) se GERENTE_PROJETO")
    ativo: bool = Field(True, description="Status ativo do usuário no sistema")


class UsuarioUpdateSchema(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    departamento: Optional[str] = None
    perfil: Optional[str] = None
    projeto_atribuido: Optional[str] = None
    ativo: Optional[bool] = None


@router.get("/admin/usuarios", summary="Listar usuários RBAC do sistema local")
async def list_usuarios(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(verify_admin_group),
):
    stmt = select(UsuarioSistema).order_by(UsuarioSistema.nome)
    res = await db.execute(stmt)
    users = res.scalars().all()
    return [u.to_dict() for u in users]


@router.post("/admin/usuarios", summary="Cadastrar novo usuário no banco local")
async def create_usuario(
    payload: UsuarioCreateSchema,
    request: Request,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(verify_admin_group),
):
    clean_username = payload.username.strip().lower()

    # Valida se já existe
    stmt = select(UsuarioSistema).where(UsuarioSistema.username == clean_username)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Usuário '{clean_username}' já está cadastrado no sistema.",
        )

    # Valida projeto se perfil for GERENTE_PROJETO
    if payload.perfil == "GERENTE_PROJETO":
        if payload.projeto_atribuido is None or str(payload.projeto_atribuido) not in PROJECTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Para o perfil Gerente de Projeto, é obrigatório associar a um dos 5 projetos (0 a 4).",
            )

    novo_usuario = UsuarioSistema(
        username=clean_username,
        nome=payload.nome.strip(),
        email=payload.email.strip() if payload.email else None,
        departamento=payload.departamento.strip() if payload.departamento else None,
        perfil=payload.perfil.strip(),
        projeto_atribuido=str(payload.projeto_atribuido) if payload.projeto_atribuido is not None else None,
        ativo=payload.ativo,
    )
    db.add(novo_usuario)
    await db.commit()
    await db.refresh(novo_usuario)

    # Auditoria
    client_ip = request.client.host if request.client else "127.0.0.1"
    await registrar_auditoria(
        db=db,
        usuario=current_user.get("username", "ADMIN"),
        categoria="CONFIGURACAO",
        acao="CRIAR_USUARIO",
        recurso=f"usuario:{novo_usuario.username}:id:{novo_usuario.id}",
        dados_anteriores=None,
        dados_novos=novo_usuario.to_dict(),
        ip_origem=client_ip,
    )

    return novo_usuario.to_dict()


@router.put("/admin/usuarios/{id}", summary="Atualizar usuário e perfil no banco local")
async def update_usuario(
    payload: UsuarioUpdateSchema,
    request: Request,
    id: int = Path(..., description="ID do usuário"),
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(verify_admin_group),
):
    stmt = select(UsuarioSistema).where(UsuarioSistema.id == id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    dados_anteriores = user.to_dict()

    if payload.nome is not None:
        user.nome = payload.nome.strip()
    if payload.email is not None:
        user.email = payload.email.strip()
    if payload.departamento is not None:
        user.departamento = payload.departamento.strip()
    if payload.perfil is not None:
        user.perfil = payload.perfil.strip()
    if payload.projeto_atribuido is not None:
        user.projeto_atribuido = str(payload.projeto_atribuido).strip()
    if payload.ativo is not None:
        user.ativo = payload.ativo

    # Validação do perfil Gerente de Projeto
    if user.perfil == "GERENTE_PROJETO" and (not user.projeto_atribuido or user.projeto_atribuido not in PROJECTS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Para o perfil Gerente de Projeto, é obrigatório associar a um dos 5 projetos válidos.",
        )

    await db.commit()
    await db.refresh(user)

    client_ip = request.client.host if request.client else "127.0.0.1"
    await registrar_auditoria(
        db=db,
        usuario=current_user.get("username", "ADMIN"),
        categoria="CONFIGURACAO",
        acao="ATUALIZAR_USUARIO",
        recurso=f"usuario:{user.username}:id:{user.id}",
        dados_anteriores=dados_anteriores,
        dados_novos=user.to_dict(),
        ip_origem=client_ip,
    )

    return user.to_dict()


@router.delete("/admin/usuarios/{id}", summary="Excluir usuário do banco local")
async def delete_usuario(
    request: Request,
    id: int = Path(..., description="ID do usuário"),
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(verify_admin_group),
):
    stmt = select(UsuarioSistema).where(UsuarioSistema.id == id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    dados_excluidos = user.to_dict()
    await db.delete(user)
    await db.commit()

    client_ip = request.client.host if request.client else "127.0.0.1"
    await registrar_auditoria(
        db=db,
        usuario=current_user.get("username", "ADMIN"),
        categoria="CONFIGURACAO",
        acao="EXCLUIR_USUARIO",
        recurso=f"usuario:{user.username}:id:{id}",
        dados_anteriores=dados_excluidos,
        dados_novos=None,
        ip_origem=client_ip,
    )

    return {"status": "success", "message": f"Usuário '{user.username}' removido com sucesso."}


class BimestreConfigUpdateSchema(BaseModel):
    ativo: bool


@router.get("/admin/bimestres-config", summary="Listar configurações de disponibilidade de bimestres")
async def get_bimestres_config(
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(verify_admin_group),
):
    await init_default_bimestres(db)
    stmt = select(ConfiguracaoBimestre).order_by(ConfiguracaoBimestre.periodo_code.asc())
    res = await db.execute(stmt)
    bimestres = res.scalars().all()
    return [b.to_dict() for b in bimestres]


@router.put("/admin/bimestres-config/{periodo_code}", summary="Atualizar status de disponibilidade de um bimestre")
async def update_bimestre_config(
    request: Request,
    payload: BimestreConfigUpdateSchema,
    periodo_code: str = Path(..., description="Código do período (0 a 5)"),
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(verify_admin_group),
):
    await init_default_bimestres(db)
    stmt = select(ConfiguracaoBimestre).where(ConfiguracaoBimestre.periodo_code == periodo_code)
    res = await db.execute(stmt)
    bimestre = res.scalars().first()
    if not bimestre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bimestre não encontrado.")

    dados_anteriores = bimestre.to_dict()
    bimestre.ativo = payload.ativo
    bimestre.updated_by = current_user.get("username", "ADMIN")

    await db.commit()
    await db.refresh(bimestre)

    client_ip = request.client.host if request.client else "127.0.0.1"
    await registrar_auditoria(
        db=db,
        usuario=current_user.get("username", "ADMIN"),
        categoria="CONFIGURACAO",
        acao="ATUALIZAR_DISPONIBILIDADE_BIMESTRE",
        recurso=f"bimestre:{periodo_code}",
        dados_anteriores=dados_anteriores,
        dados_novos=bimestre.to_dict(),
        ip_origem=client_ip,
    )

    return bimestre.to_dict()

