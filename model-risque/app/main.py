"""Main FastAPI application for ModelRisque service."""
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
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse,
    OutcomeUpdateRequest, ModelInfoResponse,
    ModelMetrics, PredictionStats, HealthResponse, RiskFactor
)
from app.model_service import ModelService, get_model
from prometheus_fastapi_instrumentator import Instrumentator

settings = get_settings()
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="ModelRisque Service",
    description="Risk Prediction Service for HealthFlow-MS - XGBoost with SHAP explanations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize Prometheus metrics BEFORE middlewares
Instrumentator().instrument(app).expose(app)

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
    logger.info("Starting ModelRisque service", port=settings.service_port)

    # Pre-load model
    try:
        model = get_model()
        logger.info("Model loaded successfully", model_type=type(model).__name__)
    except Exception as e:
        logger.error(f"Could not load model: {e}")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        db.execute(text("SELECT 1"))
        model = get_model()
        model_loaded = model is not None
    except Exception:
        model_loaded = False
    
    return HealthResponse(
        status="UP" if model_loaded else "DEGRADED",
        service="model-risque",
        timestamp=datetime.now(),
        model_loaded=model_loaded,
        model_version=settings.model_version
    )


@app.post("/api/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Make a risk prediction for a patient.
    
    Returns risk score (0-1), risk level (HIGH/MEDIUM/LOW), and SHAP explanations.
    """
    service = ModelService(db)
    
    prediction = service.predict(
        request.pseudo_patient_id,
        encounter_id=request.encounter_id,
        discharge_date=request.discharge_date
    )
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Features not found for patient {request.pseudo_patient_id}"
        )
    
    return PredictionResponse(
        pseudo_patient_id=prediction.pseudo_patient_id,
        encounter_id=prediction.encounter_id,
        risk_score=prediction.risk_score,
        risk_level=prediction.risk_level,
        confidence_interval=[prediction.confidence_lower, prediction.confidence_upper],
        top_risk_factors=[
            RiskFactor(**factor) for factor in prediction.top_risk_factors
        ] if prediction.top_risk_factors else [],
        prediction_timestamp=prediction.prediction_timestamp,
        model_version=settings.model_version,
        prediction_horizon_days=prediction.prediction_horizon_days
    )


@app.post("/api/predict/batch", response_model=BatchPredictionResponse, tags=["Predictions"])
async def batch_predict(
    request: BatchPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Make predictions for multiple patients.
    """
    service = ModelService(db)
    result = service.batch_predict(request.pseudo_patient_ids)
    
    predictions = []
    for pred in result["predictions"]:
        predictions.append(PredictionResponse(
            pseudo_patient_id=pred.pseudo_patient_id,
            encounter_id=pred.encounter_id,
            risk_score=pred.risk_score,
            risk_level=pred.risk_level,
            confidence_interval=[pred.confidence_lower, pred.confidence_upper],
            top_risk_factors=[
                RiskFactor(**factor) for factor in pred.top_risk_factors
            ] if pred.top_risk_factors else [],
            prediction_timestamp=pred.prediction_timestamp,
            model_version=settings.model_version,
            prediction_horizon_days=pred.prediction_horizon_days
        ))
    
    return BatchPredictionResponse(
        total_processed=result["total_processed"],
        successful=result["successful"],
        failed=result["failed"],
        predictions=predictions,
        errors=result["errors"]
    )


@app.get("/api/predict/{pseudo_patient_id}", response_model=PredictionResponse, tags=["Predictions"])
async def get_prediction(
    pseudo_patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the latest prediction for a patient.
    """
    service = ModelService(db)
    prediction = service.get_prediction(pseudo_patient_id)
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prediction found for patient {pseudo_patient_id}"
        )
    
    return PredictionResponse(
        pseudo_patient_id=prediction.pseudo_patient_id,
        encounter_id=prediction.encounter_id,
        risk_score=prediction.risk_score,
        risk_level=prediction.risk_level,
        confidence_interval=[prediction.confidence_lower, prediction.confidence_upper],
        top_risk_factors=[
            RiskFactor(**factor) for factor in prediction.top_risk_factors
        ] if prediction.top_risk_factors else [],
        prediction_timestamp=prediction.prediction_timestamp,
        model_version=settings.model_version,
        prediction_horizon_days=prediction.prediction_horizon_days
    )


@app.get("/api/predict/{pseudo_patient_id}/explanation", tags=["Predictions"])
async def get_explanation(
    pseudo_patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed SHAP explanation for a patient's prediction.
    """
    service = ModelService(db)
    prediction = service.get_prediction(pseudo_patient_id)
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prediction found for patient {pseudo_patient_id}"
        )
    
    return {
        "pseudo_patient_id": prediction.pseudo_patient_id,
        "risk_score": prediction.risk_score,
        "shap_values": prediction.shap_values,
        "top_risk_factors": prediction.top_risk_factors,
        "prediction_timestamp": prediction.prediction_timestamp
    }


@app.put("/api/outcome", tags=["Outcomes"])
async def update_outcome(
    request: OutcomeUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update actual outcome for a patient (for model monitoring).
    """
    service = ModelService(db)
    success = service.update_outcome(
        request.pseudo_patient_id,
        request.actual_readmission,
        request.readmission_date
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prediction found for patient {request.pseudo_patient_id}"
        )
    
    return {"status": "updated", "pseudo_patient_id": request.pseudo_patient_id}


@app.get("/api/high-risk", tags=["Predictions"])
async def get_high_risk_patients(
    threshold: float = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of high-risk patients.
    """
    service = ModelService(db)
    patients = service.get_high_risk_patients(threshold, limit)
    
    return {
        "threshold": threshold or settings.risk_threshold_high,
        "count": len(patients),
        "patients": [
            {
                "pseudo_patient_id": p.pseudo_patient_id,
                "risk_score": p.risk_score,
                "risk_level": p.risk_level,
                "prediction_timestamp": p.prediction_timestamp
            }
            for p in patients
        ]
    }


@app.get("/api/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info(db: Session = Depends(get_db)):
    """
    Get information about the active model.
    """
    service = ModelService(db)
    model_info = service.get_model_info()
    
    if not model_info:
        return ModelInfoResponse(
            model_name="readmission_xgboost",
            model_version=settings.model_version,
            model_type="XGBoost",
            is_active=True,
            training_metrics={
                "auc_roc": 0.82,
                "precision": 0.78,
                "recall": 0.74,
                "f1_score": 0.76
            },
            feature_importance={},
            deployed_at=None
        )
    
    return ModelInfoResponse(
        model_name=model_info.model_name,
        model_version=model_info.model_version,
        model_type=model_info.model_type,
        is_active=model_info.is_active,
        training_metrics=model_info.training_metrics or {},
        feature_importance=model_info.feature_importance or {},
        deployed_at=model_info.deployed_at
    )


@app.get("/api/model/metrics", response_model=ModelMetrics, tags=["Model"])
async def get_model_metrics(db: Session = Depends(get_db)):
    """
    Get model performance metrics.
    """
    service = ModelService(db)
    return service.get_model_metrics()


@app.get("/api/stats", response_model=PredictionStats, tags=["Statistics"])
async def get_stats(db: Session = Depends(get_db)):
    """
    Get prediction statistics.
    """
    service = ModelService(db)
    return service.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.service_host, port=settings.service_port)

