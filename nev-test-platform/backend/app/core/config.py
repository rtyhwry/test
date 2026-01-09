"""
Application configuration settings.
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "NEV Test Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nev_test_platform"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_DB: int = 1
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # GitLab Integration
    GITLAB_URL: Optional[str] = None
    GITLAB_TOKEN: Optional[str] = None
    
    # ALM Integration
    ALM_URL: Optional[str] = None
    ALM_USERNAME: Optional[str] = None
    ALM_PASSWORD: Optional[str] = None
    
    # Artifact Repository
    ARTIFACT_REPO_URL: Optional[str] = None
    ARTIFACT_REPO_USERNAME: Optional[str] = None
    ARTIFACT_REPO_PASSWORD: Optional[str] = None
    
    # File Storage
    UPLOAD_DIR: str = "/app/uploads"
    REPORT_DIR: str = "/app/reports"
    LOG_DIR: str = "/app/logs"
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@nev-test-platform.com"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
