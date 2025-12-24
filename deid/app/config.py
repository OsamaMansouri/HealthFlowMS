"""Configuration settings for DeID service."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://healthflow:healthflow_secure_2024@localhost:5433/healthflow"
    
    # Service
    service_name: str = "deid"
    service_host: str = "0.0.0.0"
    service_port: int = 8082
    debug: bool = False
    
    # De-identification settings
    deid_salt: str = "healthflow_deid_salt_2024"
    preserve_age_groups: bool = True
    age_group_bins: list = [0, 18, 30, 45, 60, 75, 90, 120]
    date_shift_range_days: int = 30
    
    # CORS - can be set via CORS_ORIGINS env var as comma-separated string
    cors_origins: str = "http://localhost:8087,http://localhost:3000,http://localhost:8086"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""  # No prefix needed, use exact variable names


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

