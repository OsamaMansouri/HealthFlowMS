"""SQLAlchemy models for ScoreAPI service."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, JSON, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    """Users table."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), nullable=False, default='clinician')
    department = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ApiAuditLog(Base):
    """API audit log."""
    __tablename__ = "api_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    request_params = Column(JSON)
    response_status = Column(Integer)
    patient_ids_accessed = Column(ARRAY(Text))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    request_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    response_time_ms = Column(Integer)


class RiskPrediction(Base):
    """Risk predictions (read-only)."""
    __tablename__ = "risk_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True)
    pseudo_patient_id = Column(String(100), nullable=False)
    encounter_id = Column(String(100))
    model_id = Column(UUID(as_uuid=True))
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    shap_values = Column(JSON)
    top_risk_factors = Column(JSON)
    prediction_timestamp = Column(DateTime(timezone=True))
    discharge_date = Column(DateTime(timezone=True))
    prediction_horizon_days = Column(Integer)
    actual_readmission = Column(Boolean)
    actual_readmission_date = Column(DateTime(timezone=True))
    outcome_recorded_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class DeidPatient(Base):
    """De-identified patients (read-only)."""
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


