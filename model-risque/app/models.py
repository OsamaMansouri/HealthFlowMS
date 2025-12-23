"""SQLAlchemy models for ModelRisque service."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class MLModel(Base):
    """ML Model registry."""
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=False)
    model_type = Column(String(50), nullable=False)
    model_path = Column(String(500))
    hyperparameters = Column(JSON)
    training_metrics = Column(JSON)
    validation_metrics = Column(JSON)
    feature_importance = Column(JSON)
    is_active = Column(Boolean, default=False)
    trained_at = Column(DateTime(timezone=True))
    deployed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RiskPrediction(Base):
    """Risk predictions."""
    __tablename__ = "risk_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pseudo_patient_id = Column(String(100), nullable=False)
    encounter_id = Column(String(100))
    model_id = Column(UUID(as_uuid=True))
    
    # Prediction results
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    
    # SHAP explanations
    shap_values = Column(JSON)
    top_risk_factors = Column(JSON)
    
    # Metadata
    prediction_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    discharge_date = Column(DateTime(timezone=True))
    prediction_horizon_days = Column(Integer, default=30)
    
    # Outcome tracking
    actual_readmission = Column(Boolean)
    actual_readmission_date = Column(DateTime(timezone=True))
    outcome_recorded_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PatientFeatures(Base):
    """Patient features (read-only)."""
    __tablename__ = "patient_features"

    id = Column(UUID(as_uuid=True), primary_key=True)
    pseudo_patient_id = Column(String(100), nullable=False)
    encounter_id = Column(String(100))
    feature_version = Column(String(20), nullable=False)
    
    # Demographics
    age_at_admission = Column(Integer)
    gender_encoded = Column(Integer)
    
    # Clinical Features
    length_of_stay = Column(Integer)
    previous_admissions_30d = Column(Integer)
    previous_admissions_90d = Column(Integer)
    previous_admissions_365d = Column(Integer)
    charlson_comorbidity_index = Column(Float)
    elixhauser_score = Column(Float)
    
    # Vital Signs
    heart_rate_last = Column(Float)
    blood_pressure_systolic_last = Column(Float)
    blood_pressure_diastolic_last = Column(Float)
    respiratory_rate_last = Column(Float)
    temperature_last = Column(Float)
    oxygen_saturation_last = Column(Float)
    
    # Lab Values
    hemoglobin_last = Column(Float)
    creatinine_last = Column(Float)
    sodium_last = Column(Float)
    potassium_last = Column(Float)
    glucose_last = Column(Float)
    wbc_count_last = Column(Float)
    
    # NLP Features
    nlp_sentiment_score = Column(Float)
    nlp_urgency_score = Column(Float)
    nlp_complexity_score = Column(Float)
    nlp_entities_count = Column(Integer)
    nlp_medication_mentions = Column(Integer)
    nlp_symptom_mentions = Column(Integer)
    
    # Diagnosis Features
    primary_diagnosis_code = Column(String(20))
    diagnosis_count = Column(Integer)
    has_diabetes = Column(Boolean, default=False)
    has_hypertension = Column(Boolean, default=False)
    has_heart_failure = Column(Boolean, default=False)
    has_copd = Column(Boolean, default=False)
    has_ckd = Column(Boolean, default=False)
    has_cancer = Column(Boolean, default=False)
    
    # Medication Features
    medication_count = Column(Integer)
    high_risk_medication_count = Column(Integer)
    
    # Procedure Features
    procedure_count = Column(Integer)
    surgical_procedure = Column(Boolean, default=False)
    
    # Discharge Features
    discharge_disposition = Column(String(50))
    discharge_to_home = Column(Boolean)
    
    computed_at = Column(DateTime(timezone=True))


