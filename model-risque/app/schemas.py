"""Pydantic schemas for ModelRisque service."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class RiskFactor(BaseModel):
    """Individual risk factor with SHAP explanation."""
    feature: str
    impact: float = Field(..., description="SHAP value impact on prediction")
    value: Any = Field(..., description="Actual feature value")
    direction: str = Field(..., description="'increases' or 'decreases' risk")


class PredictionRequest(BaseModel):
    """Request for risk prediction."""
    pseudo_patient_id: str = Field(..., description="De-identified patient ID")
    encounter_id: Optional[str] = Field(None, description="Specific encounter ID")
    discharge_date: Optional[datetime] = Field(None, description="Discharge date")


class PredictionResponse(BaseModel):
    """Response with risk prediction."""
    pseudo_patient_id: str
    encounter_id: Optional[str]
    risk_score: float = Field(..., ge=0, le=1, description="Risk score (0-1)")
    risk_level: str = Field(..., description="HIGH, MEDIUM, or LOW")
    confidence_interval: List[float] = Field(..., description="[lower, upper] bounds")
    top_risk_factors: List[RiskFactor]
    prediction_timestamp: datetime
    model_version: str
    prediction_horizon_days: int = 30


class BatchPredictionRequest(BaseModel):
    """Request for batch predictions."""
    pseudo_patient_ids: List[str]
    encounter_id: Optional[str] = None


class BatchPredictionResponse(BaseModel):
    """Response for batch predictions."""
    total_processed: int
    successful: int
    failed: int
    predictions: List[PredictionResponse]
    errors: List[Dict[str, str]] = Field(default_factory=list)


class OutcomeUpdateRequest(BaseModel):
    """Request to update actual outcome."""
    pseudo_patient_id: str
    actual_readmission: bool
    readmission_date: Optional[datetime] = None


class ModelInfoResponse(BaseModel):
    """Model information response."""
    model_name: str
    model_version: str
    model_type: str
    is_active: bool
    training_metrics: Dict[str, float]
    feature_importance: Dict[str, float]
    deployed_at: Optional[datetime]


class ModelMetrics(BaseModel):
    """Model performance metrics."""
    auc_roc: float
    precision: float
    recall: float
    f1_score: float
    brier_score: float
    total_predictions: int
    predictions_with_outcomes: int


class PredictionStats(BaseModel):
    """Prediction statistics."""
    total_predictions: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    average_risk_score: float
    predictions_today: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: datetime
    model_loaded: bool
    model_version: str


