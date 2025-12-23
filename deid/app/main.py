"""Main FastAPI application for DeID service."""
from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog

from app.config import get_settings
from app.database import get_db, engine, Base
from app.schemas import (
    PatientDeIdRequest, PatientDeIdResponse,
    BatchDeIdRequest, BatchDeIdResponse,
    DeidMappingResponse, AuditLogEntry,
    DeIdStats, HealthResponse
)
from app.deid_service import DeIdentificationService

settings = get_settings()
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="DeID Service",
    description="De-identification Service for HealthFlow-MS - HIPAA Safe Harbor compliant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("Starting DeID service", port=settings.service_port)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return HealthResponse(
        status="UP" if db_status == "connected" else "DEGRADED",
        service="deid",
        timestamp=datetime.now(),
        database=db_status
    )


@app.post("/api/deid/patient", response_model=PatientDeIdResponse, tags=["De-identification"])
async def deidentify_patient(
    request: PatientDeIdRequest,
    db: Session = Depends(get_db)
):
    """
    De-identify a single patient.
    
    Removes direct identifiers and generalizes quasi-identifiers according to
    HIPAA Safe Harbor guidelines.
    """
    service = DeIdentificationService(db)
    
    deid_patient, removed_fields, modified_fields = service.deidentify_patient(
        request.patient_fhir_id
    )
    
    if not deid_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {request.patient_fhir_id} not found"
        )
    
    return PatientDeIdResponse(
        pseudo_id=deid_patient.pseudo_id,
        age_group=deid_patient.age_group,
        gender=deid_patient.gender,
        deid_data=deid_patient.deid_data,
        fields_removed=removed_fields,
        fields_modified=modified_fields,
        deid_timestamp=deid_patient.deid_timestamp
    )


@app.post("/api/deid/batch", response_model=BatchDeIdResponse, tags=["De-identification"])
async def batch_deidentify(
    request: BatchDeIdRequest,
    db: Session = Depends(get_db)
):
    """
    De-identify multiple patients in batch.
    """
    service = DeIdentificationService(db)
    result = service.batch_deidentify(request.patient_fhir_ids)
    
    return BatchDeIdResponse(**result)


@app.get("/api/deid/mapping/{original_id}", response_model=DeidMappingResponse, tags=["Mapping"])
async def get_mapping(
    original_id: str,
    db: Session = Depends(get_db)
):
    """
    Get pseudo ID mapping for an original patient ID.
    
    This endpoint should be access-controlled and audited.
    """
    service = DeIdentificationService(db)
    mapping = service.get_pseudo_mapping(original_id)
    
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No mapping found for patient {original_id}"
        )
    
    return DeidMappingResponse(
        pseudo_id=mapping.pseudo_id,
        age_group=mapping.age_group,
        gender=mapping.gender,
        deid_timestamp=mapping.deid_timestamp
    )


@app.get("/api/deid/patient/{pseudo_id}", tags=["De-identification"])
async def get_deid_patient(
    pseudo_id: str,
    db: Session = Depends(get_db)
):
    """
    Get de-identified patient data by pseudo ID.
    """
    service = DeIdentificationService(db)
    patient = service.get_by_pseudo_id(pseudo_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with pseudo ID {pseudo_id} not found"
        )
    
    return {
        "pseudo_id": patient.pseudo_id,
        "age_group": patient.age_group,
        "gender": patient.gender,
        "deid_data": patient.deid_data,
        "deid_timestamp": patient.deid_timestamp
    }


@app.delete("/api/deid/patient/{original_id}", tags=["De-identification"])
async def delete_patient_data(
    original_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete all de-identified data for a patient (GDPR right to erasure).
    """
    service = DeIdentificationService(db)
    success = service.delete_patient_data(original_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {original_id} not found"
        )
    
    return {"status": "deleted", "original_id": original_id}


@app.get("/api/deid/audit", response_model=List[AuditLogEntry], tags=["Audit"])
async def get_audit_log(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get recent de-identification audit log entries.
    """
    service = DeIdentificationService(db)
    logs = service.get_audit_log(limit)
    return logs


@app.get("/api/deid/stats", response_model=DeIdStats, tags=["Statistics"])
async def get_stats(db: Session = Depends(get_db)):
    """
    Get de-identification statistics.
    """
    service = DeIdentificationService(db)
    return service.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.service_host, port=settings.service_port)

