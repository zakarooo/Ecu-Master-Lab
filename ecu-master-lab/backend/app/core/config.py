import json
import os
import secrets
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "ECU Master Lab"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    DATABASE_URL: str = "postgresql://ecu_user:ecu_password@localhost:5432/ecu_master_lab"

    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "../uploads"))
    MAX_FILE_SIZE: int = 50 * 1024 * 1024

    REDIS_URL: str = ""

    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL: str = "mistral-small-latest"

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "https://frontend-fog8mm9kk-basrhicham-9750s-projects.vercel.app", "https://frontend-beige-rho-83.vercel.app"]

    PORT: int = 8000

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v:
            return secrets.token_urlsafe(64)
        if len(v) < 32:
            raise ValueError("SECRET_KEY doit faire au moins 32 caractères")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return [s.strip() for s in v.split(",") if s.strip()]
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
