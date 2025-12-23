"""Configuration settings for ModelRisque service."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://healthflow:healthflow_secure_2024@localhost:5433/healthflow"
    
    # Service
    service_name: str = "model-risque"
    service_host: str = "0.0.0.0"
    service_port: int = 8084
    debug: bool = False
    
    # Model settings
    model_path: str = "./models/readmission_model.pkl"
    model_version: str = "v2.1.0"
    
    # Risk thresholds
    risk_threshold_high: float = 0.7
    risk_threshold_medium: float = 0.4
    
    # Feature columns for model
    feature_columns: List[str] = [
        "age_at_admission",
        "gender_encoded",
        "length_of_stay",
        "previous_admissions_30d",
        "previous_admissions_90d",
        "previous_admissions_365d",
        "charlson_comorbidity_index",
        "heart_rate_last",
        "blood_pressure_systolic_last",
        "blood_pressure_diastolic_last",
        "respiratory_rate_last",
        "temperature_last",
        "oxygen_saturation_last",
        "hemoglobin_last",
        "creatinine_last",
        "sodium_last",
        "potassium_last",
        "glucose_last",
        "wbc_count_last",
        "nlp_sentiment_score",
        "nlp_urgency_score",
        "nlp_complexity_score",
        "diagnosis_count",
        "has_diabetes",
        "has_hypertension",
        "has_heart_failure",
        "has_copd",
        "has_ckd",
        "has_cancer",
        "medication_count",
        "procedure_count",
        "discharge_to_home"
    ]
    
    # Featurizer service URL
    featurizer_service_url: str = "http://localhost:8083"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

