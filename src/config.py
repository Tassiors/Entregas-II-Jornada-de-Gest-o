"""
Módulo Centralizado de Configurações e Validação de Segredos (Settings)
=======================================================================
Garante o Padrão de Governança de Variáveis de Ambiente (Env Vars & Secrets) do HC-UFPE.
Carrega o arquivo .env e valida se os parâmetros essenciais e chaves de segurança estão corretos.
"""

import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("config")


class Settings:
    # 1. Configurações do Servidor
    ENV: str = os.getenv("ENV", "development").lower()
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info").lower()
    RAW_ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() for origin in RAW_ALLOWED_ORIGINS.split(",") if origin.strip()
    ]

    # 2. Provedores e Bancos de Dados
    PACIENTE_PROVIDER_TYPE: str = os.getenv("PACIENTE_PROVIDER_TYPE", "CSV").upper()
    APP_DB_URL: str = os.getenv("APP_DB_URL", "sqlite+aiosqlite:///data/app.db")
    SQLITE_DSN: str = os.getenv("SQLITE_DSN", "sqlite+aiosqlite:///data/app.db")
    POSTGRES_DSN: str = os.getenv("POSTGRES_DSN", "")
    ORACLE_DSN: str = os.getenv("ORACLE_DSN", "")

    # 3. Active Directory (LDAP)
    AD_URL: str = os.getenv("AD_URL", "")
    AD_BASEDN: str = os.getenv("AD_BASEDN", "DC=ebserhnet,DC=gov,DC=br")
    AD_BIND_USER: str = os.getenv("AD_BIND_USER", "")
    AD_BIND_PASSWORD: str = os.getenv("AD_BIND_PASSWORD", "")
    ADMIN_GROUP: str = os.getenv("ADMIN_GROUP", "ADMINISTRADOR")

    # 4. Segurança e Criptografia (JWT)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    JWT_EXP_HOURS: int = int(os.getenv("JWT_EXP_HOURS", "24"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXP_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXP_DAYS", "30"))
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"

    # 5. REDCap API - II Jornada de Gestão
    REDCAP_API_URL: str = os.getenv("REDCAP_API_URL", "https://redcap.ebserh.gov.br/api/")
    REDCAP_TOKEN: str = os.getenv("REDCAP_TOKEN", "CC891F928C7548C496BA3CBC07C828B4")
    REDCAP_CACHE_TTL_SECONDS: int = int(os.getenv("REDCAP_CACHE_TTL_SECONDS", "300"))

    @classmethod
    def validate_config(cls):
        """Valida a integridade das configurações e dispara avisos de segurança."""
        if cls.ENV == "production":
            if "change-in-production" in cls.JWT_SECRET or "SUA_CHAVE_SECRETA" in cls.JWT_SECRET:
                logger.error(
                    "❌ ERRO CRÍTICO DE SEGURANÇA: A variável 'JWT_SECRET' está usando a chave padrão. "
                    "Altere para uma chave secreta aleatória forte no arquivo .env antes de rodar em produção!"
                )
            if not cls.AD_URL:
                logger.warning(
                    "⚠️ AVISO: Variável 'AD_URL' não definida em produção. "
                    "O sistema está operando no modo Mock de desenvolvimento."
                )
        logger.info(f"Configurações carregadas com sucesso. Ambiente: '{cls.ENV.upper()}'")


# ── Definições de Negócio da II Jornada de Gestão ──────────────────────────────
PERIODS: Dict[str, str] = {
    "0": "Julho/Agosto 2026",
    "1": "Setembro/Outubro 2026",
    "2": "Novembro/Dezembro 2026",
    "3": "Janeiro/Fevereiro 2027",
    "4": "Março/Abril 2027",
    "5": "Maio/Junho 2027",
}

PROJECTS: Dict[str, Dict[str, Any]] = {
    "0": {
        "code": "P1",
        "short": "HC-UFPE 360°",
        "name": "HC-UFPE 360°: Qualificação do Acesso e da Capacidade Assistencial",
        "color": "#1565C0",
        "color2": "#0288D1",
        "icon": "🔵",
    },
    "1": {
        "code": "P2",
        "short": "Jornada do Paciente",
        "name": "Jornada do Paciente Centrada no Cuidado Humanizado",
        "color": "#00796B",
        "color2": "#26A69A",
        "icon": "🩺",
    },
    "2": {
        "code": "P3",
        "short": "Logística de Suprimentos",
        "name": "Logística de Suprimentos para a Eficiência do Apoio Diagnóstico",
        "color": "#6A1B9A",
        "color2": "#AB47BC",
        "icon": "📦",
    },
    "3": {
        "code": "P4",
        "short": "Valorização do Trabalhador",
        "name": "Valorização do Trabalhador e Bem-Estar no Trabalho",
        "color": "#E65100",
        "color2": "#FF8F00",
        "icon": "👷",
    },
    "4": {
        "code": "P5",
        "short": "Qualidade da Preceptoria",
        "name": "Qualidade da Preceptoria e Integração Ensino-Assistência",
        "color": "#2E7D32",
        "color2": "#66BB6A",
        "icon": "🎓",
    },
}

DELIVERIES: Dict[str, Dict[str, str]] = {
    "0": {
        "ent1": "Padronização dos Protocolos de perfis assistenciais, por clínica, de acesso, triagem e permanência.",
        "ent2": "Governança e Estruturação da Regulação Interna.",
    },
    "1": {
        "ent1": "Fluxos institucionais de resposta para cada categoria de cancelamento de consulta.",
        "ent2": "Solução para confirmação prévia de consultas e procedimentos.",
    },
    "2": {
        "ent1": "Criação de comitê temporário para governança da comunicação da cadeia de suprimentos.",
        "ent2": "Ferramenta para divulgação das informações da cadeia da comunicação.",
    },
    "3": {
        "ent1": "Diagnóstico da Pesquisa de Clima.",
        "ent2": "Banco de movimentação interna.",
    },
    "4": {
        "ent1": "I Fórum de Boas Práticas em Preceptoria.",
        "ent2": "Capacitação obrigatória e direcionada, específica para gestores para funcionarem como facilitadores de planejamento em formação em preceptoria.",
    },
}

PROJ_SUFFIX: Dict[str, str] = {
    "0": "1",
    "1": "2",
    "2": "3",
    "3": "4",
    "4": "5",
}

# Instância global de configurações
settings = Settings()
settings.validate_config()