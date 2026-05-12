"""
GestiÃ³n de configuraciÃ³n
Cargar configuraciÃ³n uniformemente desde el archivo .env en la raÃ­z del proyecto
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Cargar el archivo .env desde la raÃ­z del proyecto
# Ruta: MiroFish/.env (relativo a backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), "../../.env")

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    # Si no existe .env en la raÃ­z, intentar cargar variables de entorno (para producciÃ³n)
    load_dotenv(override=True)


class Config:
    """Clase de configuraciÃ³n Flask"""

    # ConfiguraciÃ³n Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "mirofish-secret-key")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "youworld_session")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"

    # ConfiguraciÃ³n JSON - Deshabilitar escape ASCII, mostrar chino directamente (en lugar de formato \uXXXX)
    JSON_AS_ASCII = False

    # ConfiguraciÃ³n LLM (usar formato OpenAI uniforme)
    LLM_API_KEY = os.environ.get("LLM_API_KEY")
    LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.z.ai/api/paas/v4")
    LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "glm-4.5")

    # ConfiguraciÃ³n LLM Fallback (cuando el principal falla)
    LLM_FALLBACK_API_KEY = os.environ.get("LLM_FALLBACK_API_KEY")
    LLM_FALLBACK_BASE_URL = os.environ.get(
        "LLM_FALLBACK_BASE_URL", "https://api.minimax.io/v1"
    )
    LLM_FALLBACK_MODEL = os.environ.get("LLM_FALLBACK_MODEL", "MiniMax-M2.5")

    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://youworld:youworld@localhost:5432/youworld")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")

    # ConfiguraciÃ³n Zep
    ZEP_API_KEY = os.environ.get("ZEP_API_KEY")

    # ConfiguraciÃ³n Memory Backend
    MEMORY_BACKEND = os.environ.get("MEMORY_BACKEND", "zep")

    # Neo4j (solo para graphiti)
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

    # Graphiti LLM Provider: zai | minimax | openai
    GRAPHITI_LLM_PROVIDER = os.environ.get("GRAPHITI_LLM_PROVIDER", "zai")

    # ConfiguraciÃ³n de subida de archivos
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../uploads")
    ALLOWED_EXTENSIONS = {"pdf", "md", "txt", "markdown"}

    # ConfiguraciÃ³n de procesamiento de texto
    DEFAULT_CHUNK_SIZE = 500  # TamaÃ±o de fragmento predeterminado
    DEFAULT_CHUNK_OVERLAP = 50  # TamaÃ±o de superposiciÃ³n predeterminado

    # ConfiguraciÃ³n de simulaciÃ³n OASIS
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get("OASIS_DEFAULT_MAX_ROUNDS", "10"))
    OASIS_SIMULATION_DATA_DIR = os.path.join(
        os.path.dirname(__file__), "../uploads/simulations"
    )

    # Timeout de wall-clock para simulaciones (previene simulaciones colgadas)
    SIMULATION_MAX_WALL_CLOCK_SECONDS = float(
        os.environ.get("SIMULATION_MAX_WALL_CLOCK_SECONDS", "3600")
    )

    # ConfiguraciÃ³n de acciones disponibles de plataforma OASIS
    OASIS_TWITTER_ACTIONS = [
        "CREATE_POST",
        "LIKE_POST",
        "REPOST",
        "FOLLOW",
        "DO_NOTHING",
        "QUOTE_POST",
    ]
    OASIS_REDDIT_ACTIONS = [
        "LIKE_POST",
        "DISLIKE_POST",
        "CREATE_POST",
        "CREATE_COMMENT",
        "LIKE_COMMENT",
        "DISLIKE_COMMENT",
        "SEARCH_POSTS",
        "SEARCH_USER",
        "TREND",
        "REFRESH",
        "DO_NOTHING",
        "FOLLOW",
        "MUTE",
    ]

    # ConfiguraciÃ³n de Report Agent
    REPORT_AGENT_MAX_TOOL_CALLS = int(
        os.environ.get("REPORT_AGENT_MAX_TOOL_CALLS", "5")
    )
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(
        os.environ.get("REPORT_AGENT_MAX_REFLECTION_ROUNDS", "2")
    )
    REPORT_AGENT_TEMPERATURE = float(os.environ.get("REPORT_AGENT_TEMPERATURE", "0.5"))

    @classmethod
    def validate(cls):
        """Validar configuraciones necesarias"""
        errors = []
        warnings = []

        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY no estÃ¡ configurado (CRÃTICO)")

        if cls.MEMORY_BACKEND == "zep":
            if not cls.ZEP_API_KEY:
                errors.append("ZEP_API_KEY requerido para backend=zep (CRÃTICO)")
        elif cls.MEMORY_BACKEND == "graphiti":
            if not cls.NEO4J_PASSWORD or cls.NEO4J_PASSWORD == "password":
                warnings.append(
                    "NEO4J_PASSWORD no configurado o usa valor por defecto 'password'. "
                    "Se recomienda cambiarla en .env para producciÃ³n."
                )

        return {"errors": errors, "warnings": warnings}



