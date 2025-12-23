"""Main FastAPI application for Featurizer service."""
from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog

from app.config import get_settings
from app.database import get_db
from app.schemas import (
    FeatureExtractionRequest, PatientFeaturesResponse,
    BatchFeatureRequest, BatchFeatureResponse,
    NlpAnalysisRequest, NlpAnalysisResponse,
    FeatureStatsResponse, HealthResponse
)
from app.feature_service import FeatureService
from app.nlp_service import nlp_service

settings = get_settings()
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="Featurizer Service",
    description="Feature Extraction Service for HealthFlow-MS - NLP and Clinical Data Processing",
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
    logger.info("Starting Featurizer service", port=settings.service_port)
    # Pre-load NLP models
    try:
        nlp_service.ensure_models_loaded()
        logger.info("NLP models loaded successfully")
    except Exception as e:
        logger.warning(f"Could not preload NLP models: {e}")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        db.execute(text("SELECT 1"))
        db_status = True
    except Exception:
        db_status = False
    
    models_loaded = {
        "spacy": nlp_service.nlp is not None,
        "biobert": nlp_service.model is not None
    }
    
    return HealthResponse(
        status="UP" if db_status else "DEGRADED",
        service="featurizer",
        timestamp=datetime.now(),
        models_loaded=models_loaded
    )


@app.post("/api/features/extract", response_model=PatientFeaturesResponse, tags=["Features"])
async def extract_features(
    request: FeatureExtractionRequest,
    db: Session = Depends(get_db)
):
    """
    Extract features for a single patient.
    
    Combines demographic, clinical, vital signs, lab values, and NLP features.
    """
    service = FeatureService(db)
    
    features = service.extract_features(
        request.pseudo_patient_id,
        encounter_id=request.encounter_id,
        include_nlp=request.include_nlp,
        include_vitals=request.include_vitals,
        include_labs=request.include_labs
    )
    
    if not features:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {request.pseudo_patient_id} not found"
        )
    
    return features


@app.post("/api/features/batch", response_model=BatchFeatureResponse, tags=["Features"])
async def batch_extract_features(
    request: BatchFeatureRequest,
    db: Session = Depends(get_db)
):
    """
    Extract features for multiple patients.
    """
    service = FeatureService(db)
    result = service.batch_extract_features(
        request.pseudo_patient_ids,
        include_nlp=request.include_nlp,
        include_vitals=request.include_vitals,
        include_labs=request.include_labs
    )
    
    return BatchFeatureResponse(**result)


@app.get("/api/features/{pseudo_patient_id}", tags=["Features"])
async def get_patient_features(
    pseudo_patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get extracted features for a patient.
    """
    service = FeatureService(db)
    features = service.get_features_for_model(pseudo_patient_id)
    
    if not features:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Features not found for patient {pseudo_patient_id}"
        )
    
    return features


@app.post("/api/nlp/analyze", response_model=NlpAnalysisResponse, tags=["NLP"])
async def analyze_text(request: NlpAnalysisRequest):
    """
    Analyze clinical text using NLP.
    
    Extracts entities, computes sentiment, urgency, and complexity scores.
    """
    result = nlp_service.analyze_text(request.text)
    
    return NlpAnalysisResponse(
        entities=result["entities"],
        sentiment_score=result["sentiment_score"],
        urgency_score=result["urgency_score"],
        complexity_score=result["complexity_score"],
        medication_mentions=result["medication_mentions"],
        symptom_mentions=result["symptom_mentions"]
    )


@app.post("/api/nlp/entities", tags=["NLP"])
async def extract_entities(text: str):
    """
    Extract named entities from clinical text.
    """
    entities = nlp_service.extract_entities(text)
    return {"entities": entities}


@app.get("/api/features/stats", response_model=FeatureStatsResponse, tags=["Statistics"])
async def get_stats(db: Session = Depends(get_db)):
    """
    Get feature extraction statistics.
    """
    service = FeatureService(db)
    return service.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.service_host, port=settings.service_port)

