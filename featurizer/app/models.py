"""SQLAlchemy models for Featurizer service."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class PatientFeatures(Base):
    """Patient features for ML model."""
    __tablename__ = "patient_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    
    # Metadata
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class NlpEntity(Base):
    """NLP extracted entities."""
    __tablename__ = "nlp_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True))
    pseudo_patient_id = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_text = Column(String(500), nullable=False)
    entity_code = Column(String(50))
    entity_system = Column(String(200))
    confidence = Column(Float)
    start_position = Column(Integer)
    end_position = Column(Integer)
    context = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DeidPatient(Base):
    """De-identified patient (read-only)."""
    __tablename__ = "deid_patients"

    id = Column(UUID(as_uuid=True), primary_key=True)
    original_fhir_id = Column(String(100), unique=True, nullable=False)
    pseudo_id = Column(String(100), unique=True, nullable=False)
    deid_data = Column(JSON, nullable=False)
    age_group = Column(String(20))
    gender = Column(String(20))
    deid_timestamp = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class FhirEncounter(Base):
    """FHIR Encounter (read-only)."""
    __tablename__ = "fhir_encounters"

    id = Column(UUID(as_uuid=True), primary_key=True)
    fhir_id = Column(String(100), unique=True, nullable=False)
    patient_fhir_id = Column(String(100), nullable=False)
    resource_data = Column(JSON, nullable=False)
    encounter_class = Column(String(50))
    status = Column(String(50))
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    discharge_disposition = Column(String(100))
    service_type = Column(String(100))


class FhirObservation(Base):
    """FHIR Observation (read-only)."""
    __tablename__ = "fhir_observations"

    id = Column(UUID(as_uuid=True), primary_key=True)
    fhir_id = Column(String(100), unique=True, nullable=False)
    patient_fhir_id = Column(String(100), nullable=False)
    encounter_fhir_id = Column(String(100))
    resource_data = Column(JSON, nullable=False)
    code = Column(String(50))
    code_system = Column(String(200))
    display_name = Column(String(500))
    value_quantity = Column(Float)
    value_unit = Column(String(50))
    effective_date = Column(DateTime(timezone=True))
    category = Column(String(100))


class FhirCondition(Base):
    """FHIR Condition (read-only)."""
    __tablename__ = "fhir_conditions"

    id = Column(UUID(as_uuid=True), primary_key=True)
    fhir_id = Column(String(100), unique=True, nullable=False)
    patient_fhir_id = Column(String(100), nullable=False)
    encounter_fhir_id = Column(String(100))
    resource_data = Column(JSON, nullable=False)
    code = Column(String(50))
    code_system = Column(String(200))
    display_name = Column(String(500))
    clinical_status = Column(String(50))
    verification_status = Column(String(50))
    onset_date = Column(DateTime(timezone=True))


class ClinicalNote(Base):
    """Clinical notes for NLP."""
    __tablename__ = "clinical_notes"

    id = Column(UUID(as_uuid=True), primary_key=True)
    patient_fhir_id = Column(String(100), nullable=False)
    encounter_fhir_id = Column(String(100))
    note_type = Column(String(100))
    note_text = Column(Text, nullable=False)
    author = Column(String(200))
    recorded_at = Column(DateTime(timezone=True))


