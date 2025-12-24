"""Pydantic schemas for ScoreAPI service."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


# Auth schemas
class LoginRequest(BaseModel):
    """Login request."""
    username: str
    password: str


class UserResponse(BaseModel):
    """User information response."""
    id: UUID
    username: str
    email: str
    full_name: Optional[str]
    role: str
    department: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response after login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class UserCreateRequest(BaseModel):
    """User creation request."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = Field(default="clinician")
    department: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """User update request."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


# Risk score schemas
class RiskFactor(BaseModel):
    """Risk factor with impact."""
    feature: str
    impact: float
    value: Any
    direction: str


class RiskScoreResponse(BaseModel):
    """Risk score response."""
    patient_id: str
    risk_score: float
    risk_level: str
    prediction_date: datetime
    discharge_date: Optional[datetime]
    top_risk_factors: List[RiskFactor]
    confidence_interval: List[float]
    model_version: str


class PatientRiskSummary(BaseModel):
    """Patient risk summary."""
    patient_id: str
    age_group: Optional[str]
    gender: Optional[str]
    risk_score: Optional[float]
    risk_level: Optional[str]
    last_prediction_date: Optional[datetime]


class HighRiskPatientsResponse(BaseModel):
    """High risk patients response."""
    threshold: float
    count: int
    patients: List[PatientRiskSummary]


class RiskExplanationResponse(BaseModel):
    """Detailed risk explanation."""
    patient_id: str
    risk_score: float
    risk_level: str
    shap_values: Dict[str, float]
    top_risk_factors: List[RiskFactor]
    prediction_date: datetime
    interpretation: str


# Dashboard schemas
class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_patients: int
    high_risk_patients: int
    medium_risk_patients: int
    low_risk_patients: int
    predictions_today: int
    average_risk_score: float
    model_accuracy: float


class AuditLogEntry(BaseModel):
    """Audit log entry."""
    id: UUID
    user_id: Optional[UUID]
    endpoint: str
    method: str
    request_timestamp: datetime
    response_status: Optional[int]
    response_time_ms: Optional[int]
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: datetime
    version: str
    dependencies: Dict[str, str]


# Patient creation schema
class PatientCreateRequest(BaseModel):
    """FHIR Patient creation request."""
    resourceType: str = "Patient"
    name: List[Dict[str, Any]] = Field(..., description="Patient name(s)")
    gender: Optional[str] = Field(None, description="Patient gender (male, female, other, unknown)")
    birthDate: Optional[str] = Field(None, description="Patient birth date (YYYY-MM-DD)")
    identifier: Optional[List[Dict[str, Any]]] = None
    telecom: Optional[List[Dict[str, Any]]] = None
    address: Optional[List[Dict[str, Any]]] = None
    # Allow any other FHIR Patient fields
    class Config:
        extra = "allow"


class PatientCreateResponse(BaseModel):
    """Patient creation response."""
    id: str
    resourceType: str
    status: str = "created"

