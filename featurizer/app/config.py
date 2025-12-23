"""Configuration settings for Featurizer service."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://healthflow:healthflow_secure_2024@localhost:5433/healthflow"
    
    # Service
    service_name: str = "featurizer"
    service_host: str = "0.0.0.0"
    service_port: int = 8083
    debug: bool = False
    
    # Model settings
    model_cache_dir: str = "./models"
    biobert_model: str = "dmis-lab/biobert-base-cased-v1.2"
    spacy_model: str = "en_core_web_sm"
    
    # Feature extraction settings
    feature_version: str = "v1.0"
    
    # Vital signs codes (LOINC)
    vital_signs_codes: dict = {
        "heart_rate": "8867-4",
        "blood_pressure_systolic": "8480-6",
        "blood_pressure_diastolic": "8462-4",
        "respiratory_rate": "9279-1",
        "temperature": "8310-5",
        "oxygen_saturation": "2708-6"
    }
    
    # Lab codes (LOINC)
    lab_codes: dict = {
        "hemoglobin": "718-7",
        "creatinine": "2160-0",
        "sodium": "2951-2",
        "potassium": "2823-3",
        "glucose": "2345-7",
        "wbc": "6690-2"
    }
    
    # Comorbidity ICD-10 codes
    comorbidity_codes: dict = {
        "diabetes": ["E10", "E11", "E13"],
        "hypertension": ["I10", "I11", "I12", "I13"],
        "heart_failure": ["I50"],
        "copd": ["J44"],
        "ckd": ["N18"],
        "cancer": ["C"]
    }
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

