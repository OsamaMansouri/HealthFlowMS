"""Configuration settings for AuditFairness service."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://healthflow:healthflow_secure_2024@localhost:5433/healthflow"
    
    # Service
    service_name: str = "audit-fairness"
    service_host: str = "0.0.0.0"
    service_port: int = 8086
    debug: bool = False
    
    # Dash settings
    dash_debug: bool = False
    
    # Fairness thresholds
    demographic_parity_threshold: float = 0.8
    equalized_odds_threshold: float = 0.8
    calibration_threshold: float = 0.1
    
    # Protected attributes
    protected_attributes: List[str] = ["gender", "age_group"]
    
    # Model monitoring
    drift_threshold: float = 0.1
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

