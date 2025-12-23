"""Pydantic schemas for DeID service."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class PatientDeIdRequest(BaseModel):
    """Request to de-identify a patient."""
    patient_fhir_id: str = Field(..., description="Original FHIR patient ID")
    include_encounters: bool = Field(default=True, description="Include related encounters")
    include_observations: bool = Field(default=True, description="Include related observations")


class PatientDeIdResponse(BaseModel):
    """Response after de-identification."""
    pseudo_id: str = Field(..., description="Generated pseudo identifier")
    age_group: Optional[str] = Field(None, description="Age group (e.g., '45-60')")
    gender: Optional[str] = Field(None, description="Gender (preserved)")
    deid_data: Dict[str, Any] = Field(..., description="De-identified patient data")
    fields_removed: List[str] = Field(default_factory=list, description="List of removed fields")
    fields_modified: List[str] = Field(default_factory=list, description="List of modified fields")
    deid_timestamp: datetime = Field(..., description="Timestamp of de-identification")


class BatchDeIdRequest(BaseModel):
    """Request to de-identify multiple patients."""
    patient_fhir_ids: List[str] = Field(..., description="List of FHIR patient IDs")
    include_encounters: bool = Field(default=True)
    include_observations: bool = Field(default=True)


class BatchDeIdResponse(BaseModel):
    """Response for batch de-identification."""
    total_processed: int
    successful: int
    failed: int
    results: List[PatientDeIdResponse]
    errors: List[Dict[str, str]] = Field(default_factory=list)


class DeidMappingResponse(BaseModel):
    """Response for pseudo ID mapping lookup."""
    pseudo_id: str
    age_group: Optional[str]
    gender: Optional[str]
    deid_timestamp: datetime
    
    class Config:
        from_attributes = True


class AuditLogEntry(BaseModel):
    """Audit log entry response."""
    id: UUID
    operation: str
    entity_type: str
    original_id: Optional[str]
    pseudo_id: Optional[str]
    fields_modified: Optional[Dict[str, Any]]
    performed_at: datetime
    
    class Config:
        from_attributes = True


class DeIdStats(BaseModel):
    """De-identification statistics."""
    total_patients_deid: int
    total_operations: int
    operations_today: int
    last_operation_at: Optional[datetime]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: datetime
    database: str = "connected"


