"""SQLAlchemy models for AuditFairness service."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class FairnessMetrics(Base):
    """Fairness metrics over time."""
    __tablename__ = "fairness_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True))
    metric_date = Column(Date, nullable=False)
    
    # Overall metrics
    total_predictions = Column(Integer)
    overall_auc = Column(Float)
    overall_accuracy = Column(Float)
    overall_precision = Column(Float)
    overall_recall = Column(Float)
    overall_f1 = Column(Float)
    brier_score = Column(Float)
    
    # Fairness metrics
    demographic_parity_ratio = Column(Float)
    equalized_odds_ratio = Column(Float)
    
    # Group metrics
    metrics_by_age_group = Column(JSON)
    metrics_by_gender = Column(JSON)
    metrics_by_ethnicity = Column(JSON)
    metrics_by_department = Column(JSON)
    
    # Drift detection
    feature_drift_score = Column(Float)
    prediction_drift_score = Column(Float)
    data_quality_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BiasAlert(Base):
    """Bias alerts."""
    __tablename__ = "bias_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True))
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    affected_group = Column(String(100))
    metric_name = Column(String(100))
    metric_value = Column(Float)
    threshold_value = Column(Float)
    description = Column(String)
    recommendations = Column(String)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


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


class MLModel(Base):
    """ML Model registry (read-only)."""
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=False)
    model_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=False)
    training_metrics = Column(JSON)
    feature_importance = Column(JSON)
    deployed_at = Column(DateTime(timezone=True))


