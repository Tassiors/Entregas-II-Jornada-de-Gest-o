"""
Modelo SQLAlchemy para Gestão de Usuários e Perfis RBAC Locais
==============================================================
Persiste permanentemente no banco local os colaboradores autorizados,
seus papéis (ex: ADMINISTRADOR, GERENTE_PROJETO) e projetos atribuídos.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from ..resources.database import Base


class UsuarioSistema(Base):
    __tablename__ = "usuarios_sistema"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    departamento = Column(String(255), nullable=True)
    perfil = Column(String(50), nullable=False, default="CONSULTA", index=True)
    projeto_atribuido = Column(String(10), nullable=True, index=True)  # "0" a "4"
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nome": self.nome,
            "email": self.email,
            "departamento": self.departamento,
            "perfil": self.perfil,
            "projeto_atribuido": self.projeto_atribuido,
            "ativo": self.ativo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
