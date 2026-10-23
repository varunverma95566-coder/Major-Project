import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Transformer-Based NIDS & Cyber Threat Intelligence Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security & Authentication
    SECRET_KEY: str = "dev-secret-key-change-in-production-cyber-sentinel-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DEV_MODE_AUTH: bool = True  # Allows instant dev login with default credentials

    # Storage Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    ARTIFACTS_DIR: str = os.path.join(BASE_DIR, "backend", "artifacts", "models")
    SAMPLE_DATASETS_DIR: str = os.path.join(BASE_DIR, "data", "sample_datasets")
    EXPORTS_DIR: str = os.path.join(BASE_DIR, "data", "exports")
    REPORTS_DIR: str = os.path.join(BASE_DIR, "data", "reports")

    # Database Configuration (Defaults to canonical SQLite file, seamlessly switchable to Postgres/MySQL)
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'nids_platform.db').replace(os.sep, '/')}"
    
    # BigFlow-NIDS Dataset Configuration (Configurable via environment variables)
    BIGFLOW_NIDS_DIR: str = os.path.join(BASE_DIR, "BigFlow-NIDS")
    BIGFLOW_NIDS_PARQUET_DIR: str = os.path.join(BASE_DIR, "BigFlow-NIDS", "BigFlow-NIDS-V2-Merged-Parquet")
    BIGFLOW_NIDS_CSV_PATH: str = os.path.join(BASE_DIR, "BigFlow-NIDS", "BigFlow-NIDS-CSV", "BigFlow-NIDS-V2.csv")
    PRIMARY_DATASET_TYPE: str = "BigFlow-NIDS-V2"
    DEFAULT_TRAIN_SAMPLE_SIZE: int = 10000
    
    # Upload limits
    MAX_UPLOAD_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB
    
    # Model defaults (FlowTransformer defaults per specification)
    DEFAULT_EMBEDDING_DIM: int = 64
    DEFAULT_NUM_HEADS: int = 4
    DEFAULT_NUM_LAYERS: int = 2
    DEFAULT_DROPOUT: float = 0.1
    DEFAULT_BATCH_SIZE: int = 64
    DEFAULT_EPOCHS: int = 5
    DEFAULT_LEARNING_RATE: float = 0.001
    
    # Optional CTI Provider Credentials
    VIRUSTOTAL_API_KEY: str = ""
    ABUSEIPDB_API_KEY: str = ""
    
    # Optional LLM Provider Configuration
    LLM_PROVIDER: str = "simulation"  # "simulation", "openai", "anthropic"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://varunverma95566-coder.github.io",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

# Ensure directories exist
for path in [settings.ARTIFACTS_DIR, settings.SAMPLE_DATASETS_DIR, settings.EXPORTS_DIR, settings.REPORTS_DIR]:
    os.makedirs(path, exist_ok=True)
