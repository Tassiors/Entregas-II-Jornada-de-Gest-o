"""
Modelo SQLAlchemy para Respostas de Formulários da II Jornada de Gestão
=======================================================================
Armazena localmente os registros de acompanhamento das entregas dos projetos,
com auditoria, isolamento por projeto e persistência permanente no SQLite local.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from ..resources.database import Base


class FormularioResposta(Base):
    __tablename__ = "formulario_respostas"
    __table_args__ = (
        UniqueConstraint("projeto", "periodo", name="uq_formulario_projeto_periodo"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    projeto = Column(String(10), nullable=False, index=True)
    periodo = Column(String(10), nullable=False, index=True)
    var_projeto = Column(String(255), nullable=True)
    var_periodo = Column(String(100), nullable=True)
    ent1_conc = Column(String(5), nullable=False, default="1")  # "0" Sim / "1" Não
    ent1_txt = Column(Text, nullable=False)
    ent2_conc = Column(String(5), nullable=False, default="1")  # "0" Sim / "1" Não
    ent2_txt = Column(Text, nullable=False)
    form_1_complete = Column(String(5), nullable=False, default="2")
    usuario_registro = Column(String(100), nullable=False, default="SISTEMA")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "record_id": str(self.id),
            "projeto": self.projeto,
            "periodo": self.periodo,
            "var_projeto": self.var_projeto,
            "var_periodo": self.var_periodo,
            "ent1_conc": self.ent1_conc,
            "ent1_txt": self.ent1_txt,
            "ent2_conc": self.ent2_conc,
            "ent2_txt": self.ent2_txt,
            "form_1_complete": self.form_1_complete,
            "usuario_registro": self.usuario_registro,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
