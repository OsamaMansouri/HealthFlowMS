"""Pydantic schemas for Featurizer service."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class FeatureExtractionRequest(BaseModel):
    """Request to extract features for a patient."""
    pseudo_patient_id: str = Field(..., description="De-identified patient ID")
    encounter_id: Optional[str] = Field(None, description="Specific encounter ID")
    include_nlp: bool = Field(default=True, description="Include NLP features")
    include_vitals: bool = Field(default=True, description="Include vital signs")
    include_labs: bool = Field(default=True, description="Include lab values")


class PatientFeaturesResponse(BaseModel):
    """Response with extracted features."""
    pseudo_patient_id: str
    encounter_id: Optional[str]
    feature_version: str
    
    # Demographics
    age_at_admission: Optional[int]
    gender_encoded: Optional[int]
    
    # Clinical
    length_of_stay: Optional[int]
    previous_admissions_30d: Optional[int]
    previous_admissions_90d: Optional[int]
    previous_admissions_365d: Optional[int]
    charlson_comorbidity_index: Optional[float]
    
    # Vital Signs
    heart_rate_last: Optional[float]
    blood_pressure_systolic_last: Optional[float]
    blood_pressure_diastolic_last: Optional[float]
    respiratory_rate_last: Optional[float]
    temperature_last: Optional[float]
    oxygen_saturation_last: Optional[float]
    
    # Lab Values
    hemoglobin_last: Optional[float]
    creatinine_last: Optional[float]
    sodium_last: Optional[float]
    potassium_last: Optional[float]
    glucose_last: Optional[float]
    wbc_count_last: Optional[float]
    
    # NLP Features
    nlp_sentiment_score: Optional[float]
    nlp_urgency_score: Optional[float]
    nlp_complexity_score: Optional[float]
    nlp_entities_count: Optional[int]
    
    # Diagnosis
    diagnosis_count: Optional[int]
    has_diabetes: bool = False
    has_hypertension: bool = False
    has_heart_failure: bool = False
    has_copd: bool = False
    has_ckd: bool = False
    
    # Medication & Procedure
    medication_count: Optional[int]
    procedure_count: Optional[int]
    
    computed_at: datetime
    
    class Config:
        from_attributes = True


class BatchFeatureRequest(BaseModel):
    """Request to extract features for multiple patients."""
    pseudo_patient_ids: List[str]
    include_nlp: bool = True
    include_vitals: bool = True
    include_labs: bool = True


class BatchFeatureResponse(BaseModel):
    """Response for batch feature extraction."""
    total_processed: int
    successful: int
    failed: int
    features: List[PatientFeaturesResponse]
    errors: List[Dict[str, str]] = Field(default_factory=list)


class NlpEntityResponse(BaseModel):
    """NLP entity extraction response."""
    id: UUID
    pseudo_patient_id: str
    entity_type: str
    entity_text: str
    entity_code: Optional[str]
    confidence: Optional[float]
    context: Optional[str]
    
    class Config:
        from_attributes = True


class NlpAnalysisRequest(BaseModel):
    """Request for NLP analysis."""
    text: str = Field(..., description="Clinical text to analyze")
    pseudo_patient_id: Optional[str] = Field(None, description="Patient ID for saving")
    extract_entities: bool = True
    compute_sentiment: bool = True


class NlpAnalysisResponse(BaseModel):
    """Response for NLP analysis."""
    entities: List[Dict[str, Any]]
    sentiment_score: Optional[float]
    urgency_score: Optional[float]
    complexity_score: Optional[float]
    medication_mentions: int
    symptom_mentions: int


class FeatureStatsResponse(BaseModel):
    """Feature statistics response."""
    total_patients_processed: int
    total_features_computed: int
    feature_version: str
    last_computed_at: Optional[datetime]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: datetime
    models_loaded: Dict[str, bool]


