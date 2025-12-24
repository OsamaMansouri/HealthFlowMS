"""Configuration settings for ScoreAPI service."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Union
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - defaults to Docker Compose configuration
    # Can be overridden via DATABASE_URL environment variable
    # Note: pydantic-settings will read DATABASE_URL from environment if set
    database_url: str = "postgresql://healthflow:healthflow123@postgres:5432/healthflow"
    
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
    proxy_fhir_url: str = "http://proxy-fhir:8081"  # Internal Docker network URL
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # CORS - can be set via CORS_ORIGINS env var as comma-separated string
    # Use "*" for development to allow all origins (less secure but easier)
    cors_origins: str = "*"  # Change to specific origins in production
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Allow environment variables to override defaults
        env_prefix = ""  # No prefix needed, use exact variable names
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(self.cors_origins, str):
            # Handle "*" for development (allow all origins)
            if self.cors_origins.strip() == "*":
                return ["*"]
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return self.cors_origins if isinstance(self.cors_origins, list) else []


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    # Force reload from environment variables
    settings = Settings()
    # Debug: print database URL (first 50 chars to hide password)
    db_url_preview = settings.database_url[:50] + "..." if len(settings.database_url) > 50 else settings.database_url
    print(f"[Config] Database URL: {db_url_preview}")
    return settings

