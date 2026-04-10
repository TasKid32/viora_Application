"""
Configuration settings for Viora Backend.

Uses Pydantic V2 model_config instead of deprecated inner Config class.
"""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Viora API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    # SQLite: sqlite:///./viora.db
    # PostgreSQL: postgresql://user:password@host:5432/database_name
    DATABASE_URL: str = "sqlite:///./viora.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AI Models — Viora NER (ONNX) + O*NET taxonomy
    VIORA_NER_MODEL_DIR: str = "ml/viora-ner/models/exported/onnx_quantized"
    ONET_DATA_DIR: str = "ml/viora-ner/data/taxonomy/onet"
    ESCO_DATA_DIR: str = "ml/viora-ner/data/taxonomy/esco/ESCO dataset - v1.2.1 - classification - en - csv"

    # LLM API (used ONLY for chat assistant)
    GEMINI_API_KEY: Optional[str] = None

    # External APIs
    YOUTUBE_API_KEY: Optional[str] = None
    UDEMY_API_KEY: Optional[str] = None
    UDEMY_CLIENT_ID: Optional[str] = None
    UDEMY_CLIENT_SECRET: Optional[str] = None

    # Google Custom Search (course discovery across educational platforms)
    GOOGLE_SEARCH_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_CX: Optional[str] = None

    # CORS (B4 Fix — also configurable via env var CORS_ORIGINS in main.py)
    CORS_ORIGINS: Optional[str] = None

    # SMTP (Password Reset)
    SMTP_HOST: Optional[str] = None          # e.g. smtp.gmail.com
    SMTP_PORT: int = 587                     # 587 for TLS, 465 for SSL
    SMTP_USERNAME: Optional[str] = None      # e.g. your@gmail.com
    SMTP_PASSWORD: Optional[str] = None      # Use App Password for Gmail
    SMTP_FROM_EMAIL: Optional[str] = None    # Sender "from" address
    SMTP_USE_TLS: bool = True
    FRONTEND_URL: str = "http://localhost:3000"
    PASSWORD_RESET_EXPIRE_MINUTES: int = 30

    # NER Confidence Threshold (configurable via env)
    NER_CONFIDENCE_THRESHOLD: float = 0.50

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }

    @model_validator(mode="after")
    def reject_default_secret(self) -> "Settings":
        """Reject startup if SECRET_KEY is still the default — prevents JWT forgery."""
        if self.SECRET_KEY == "your-secret-key-change-in-production":
            if not self.DEBUG:
                raise RuntimeError(
                    "❌ FATAL: SECRET_KEY is using the default value! "
                    "Set a strong SECRET_KEY in your .env file before running in production. "
                    "Example: SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')"
                )
            else:
                import warnings
                warnings.warn(
                    "⚠️  SECRET_KEY is using the default value! "
                    "Set a strong SECRET_KEY in .env for production.",
                    stacklevel=2,
                )
        return self


settings = Settings()
