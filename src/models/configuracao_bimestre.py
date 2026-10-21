"""
Modelo SQLAlchemy para Configuração de Disponibilidade de Bimestres
===================================================================
Controla se cada um dos 6 bimestres da II Jornada de Gestão está
aberto para novos preenchimentos pelo gerente do projeto.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession
from ..resources.database import Base


class ConfiguracaoBimestre(Base):
    __tablename__ = "configuracao_bimestres"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    periodo_code = Column(String(10), unique=True, nullable=False, index=True)  # '0' a '5'
    periodo_nome = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    updated_by = Column(String(100), default="SISTEMA", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "periodo_code": self.periodo_code,
            "periodo_nome": self.periodo_nome,
            "ativo": self.ativo,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


async def init_default_bimestres(session: AsyncSession):
    """Garante que todos os 6 períodos bimestrais da II Jornada estejam presentes no banco."""
    from ..config import PERIODS

    for code, nome in PERIODS.items():
        stmt = select(ConfiguracaoBimestre).where(ConfiguracaoBimestre.periodo_code == code)
        res = await session.execute(stmt)
        item = res.scalars().first()
        if not item:
            novo = ConfiguracaoBimestre(
                periodo_code=code,
                periodo_nome=nome,
                ativo=True,
                updated_by="SISTEMA",
            )
            session.add(novo)
    await session.commit()
