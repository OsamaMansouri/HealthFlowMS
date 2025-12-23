"""Configuration settings for ScoreAPI service."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://healthflow:healthflow_secure_2024@localhost:5433/healthflow"
    
    # Service
    service_name: str = "score-api"
    service_host: str = "0.0.0.0"
    service_port: int = 8085
    debug: bool = False
    
    # JWT Configuration
    jwt_secret: str = "healthflow_jwt_secret_key_2024_very_secure"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 7
    
    # Internal service URLs
    model_service_url: str = "http://localhost:8084"
    featurizer_service_url: str = "http://localhost:8083"
    deid_service_url: str = "http://localhost:8082"
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8086", "http://localhost:8087"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

