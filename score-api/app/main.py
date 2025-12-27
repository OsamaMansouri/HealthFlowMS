"""Main FastAPI application for ScoreAPI service."""
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog
import httpx

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas import (
    LoginRequest, TokenResponse, RefreshTokenRequest,
    UserResponse, UserCreateRequest, UserUpdateRequest,
    RiskScoreResponse, RiskFactor, HighRiskPatientsResponse,
    PatientRiskSummary, RiskExplanationResponse,
    DashboardStats, AuditLogEntry, HealthResponse,
    PatientCreateRequest, PatientCreateResponse
)
from app.auth import (
    authenticate_user, create_access_token, create_refresh_token,
    decode_token, get_current_user, get_admin_user
)
from app.services import UserService, AuditService, RiskScoreService, PatientService
from app.models import DeidPatient, RiskPrediction
from app.cache import init_redis, get_cache, set_cache, delete_cache, redis_client
from prometheus_fastapi_instrumentator import Instrumentator

settings = get_settings()
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="ScoreAPI",
    description="Main REST API for HealthFlow-MS - Secure access to risk scores and patient data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - get allowed origins
cors_origins = settings.cors_origins_list
print(f"[CORS] Configured origins: {cors_origins}")  # Debug print
logger.info("CORS origins configured", origins=cors_origins)

# Initialize Prometheus metrics BEFORE middlewares
Instrumentator().instrument(app).expose(app)

# CORS middleware - must be added before routes
# Note: allow_origins=["*"] doesn't work with allow_credentials=True
# So we use the explicit list or handle "*" specially
if cors_origins == ["*"]:
    # For development: allow all origins (but credentials won't work)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Must be False when using "*"
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
else:
    # Production: specific origins with credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins else ["http://localhost:8087"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )


# Audit logging middleware
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """Log all API requests for audit trail."""
    start_time = time.time()
    response = await call_next(request)
    process_time = int((time.time() - start_time) * 1000)
    
    # Log to structured logger
    logger.info(
        "api_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time_ms=process_time
    )
    
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("Starting ScoreAPI service", port=settings.service_port)
    # Initialize Redis cache
    init_redis(host="redis", port=6379)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information and available endpoints."""
    return {
        "service": "HealthFlowMS ScoreAPI",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/health",
            "authentication": {
                "login": "/api/v1/auth/login",
                "refresh": "/api/v1/auth/refresh",
                "me": "/api/v1/auth/me"
            },
            "patients": {
                "list": "/api/v1/patients",
                "create": "/api/v1/patients (POST)",
                "risk_score": "/api/v1/patients/{patient_id}/risk-score",
                "risk_explanation": "/api/v1/patients/{patient_id}/risk-explanation",
                "high_risk": "/api/v1/patients/high-risk",
                "predict": "/api/v1/patients/{patient_id}/predict"
            },
            "dashboard": {
                "stats": "/api/v1/dashboard/stats"
            },
            "users": {
                "create": "/api/v1/users",
                "list": "/api/v1/users"
            },
            "audit": {
                "logs": "/api/v1/audit/logs"
            }
        },
        "message": "Visit /docs for interactive API documentation"
    }


# Health endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return HealthResponse(
        status="UP" if db_status == "connected" else "DEGRADED",
        service="score-api",
        timestamp=datetime.now(),
        version="1.0.0",
        dependencies={
            "database": db_status,
            "model_service": settings.model_service_url,
            "featurizer_service": settings.featurizer_service_url
        }
    )


# Cache test endpoint
@app.get("/api/v1/cache/test", tags=["Cache"])
async def test_cache():
    """
    Test Redis cache functionality.
    Tests set, get, and delete operations.
    """
    import time
    from app.cache import get_cache, set_cache, delete_cache, redis_client
    
    test_key = "test:cache:healthflow"
    test_value = {
        "message": "Cache test",
        "timestamp": datetime.now().isoformat(),
        "service": "score-api"
    }
    
    results = {
        "redis_connected": redis_client is not None,
        "tests": {}
    }
    
    if not redis_client:
        return {
            "status": "error",
            "message": "Redis not connected",
            "results": results
        }
    
    try:
        # Test 1: Set cache
        set_result = set_cache(test_key, test_value, expire=60)
        results["tests"]["set"] = {
            "success": set_result,
            "key": test_key
        }
        
        # Test 2: Get cache
        time.sleep(0.1)  # Small delay
        cached_value = get_cache(test_key)
        results["tests"]["get"] = {
            "success": cached_value is not None,
            "value": cached_value,
            "matches": cached_value == test_value if cached_value else False
        }
        
        # Test 3: Delete cache
        delete_result = delete_cache(test_key)
        results["tests"]["delete"] = {
            "success": delete_result
        }
        
        # Test 4: Verify deletion
        after_delete = get_cache(test_key)
        results["tests"]["verify_delete"] = {
            "success": after_delete is None
        }
        
        # Get Redis info
        try:
            info = redis_client.info()
            results["redis_info"] = {
                "version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_keys": redis_client.dbsize()
            }
        except Exception as e:
            results["redis_info"] = {"error": str(e)}
        
        all_tests_passed = all(
            test.get("success", False) 
            for test in results["tests"].values()
        )
        
        return {
            "status": "success" if all_tests_passed else "partial",
            "message": "All cache tests passed" if all_tests_passed else "Some cache tests failed",
            "results": results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Cache test failed: {str(e)}",
            "results": results
        }


# ============================================
# Authentication Endpoints
# ============================================

@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT tokens.
    """
    user = authenticate_user(db, request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user_service = UserService(db)
    user_service.update_last_login(user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_expiration_hours * 3600,
        user=UserResponse.model_validate(user)
    )


@app.post("/api/v1/auth/refresh", response_model=TokenResponse, tags=["Authentication"])
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    payload = decode_token(request.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.jwt_expiration_hours * 3600,
        user=UserResponse.model_validate(user)
    )


@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return current_user


# ============================================
# Patient Risk Score Endpoints
# ============================================

@app.get("/api/v1/patients/{patient_id}/risk-score", response_model=RiskScoreResponse, tags=["Risk Scores"])
async def get_patient_risk_score(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get risk score for a specific patient.
    """
    risk_service = RiskScoreService(db)
    prediction = risk_service.get_patient_risk_score(patient_id)
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No risk score found for patient {patient_id}"
        )
    
    return RiskScoreResponse(
        patient_id=prediction.pseudo_patient_id,
        risk_score=prediction.risk_score,
        risk_level=prediction.risk_level,
        prediction_date=prediction.prediction_timestamp,
        discharge_date=prediction.discharge_date,
        top_risk_factors=[
            RiskFactor(**factor) for factor in prediction.top_risk_factors
        ] if prediction.top_risk_factors else [],
        confidence_interval=[prediction.confidence_lower, prediction.confidence_upper],
        model_version="v2.1.0"
    )


@app.get("/api/v1/patients/{patient_id}/risk-explanation", response_model=RiskExplanationResponse, tags=["Risk Scores"])
async def get_risk_explanation(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed SHAP explanation for a patient's risk score.
    """
    risk_service = RiskScoreService(db)
    prediction = risk_service.get_patient_risk_score(patient_id)
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prediction found for patient {patient_id}"
        )
    
    # Generate interpretation text
    interpretation = f"This patient has a {prediction.risk_level} risk of readmission within 30 days "
    interpretation += f"with a score of {prediction.risk_score:.2f}. "
    
    if prediction.top_risk_factors:
        top_factor = prediction.top_risk_factors[0]
        interpretation += f"The main contributing factor is {top_factor['feature']} "
        interpretation += f"which {top_factor['direction']} the risk."
    
    return RiskExplanationResponse(
        patient_id=prediction.pseudo_patient_id,
        risk_score=prediction.risk_score,
        risk_level=prediction.risk_level,
        shap_values=prediction.shap_values or {},
        top_risk_factors=[
            RiskFactor(**factor) for factor in prediction.top_risk_factors
        ] if prediction.top_risk_factors else [],
        prediction_date=prediction.prediction_timestamp,
        interpretation=interpretation
    )


@app.get("/api/v1/patients", response_model=List[PatientRiskSummary], tags=["Patients"])
async def list_all_patients(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all patients (both FHIR and anonymized) with their risk information if available.
    """
    result = []
    
    # Get anonymized patients (deid_patients)
    patient_service = PatientService(db)
    deid_patients = patient_service.search_patients(limit=limit)
    
    for patient in deid_patients:
        summary = patient_service.get_patient_summary(patient.pseudo_id)
        if summary:
            result.append(PatientRiskSummary(**summary))
        else:
            result.append(PatientRiskSummary(
                patient_id=patient.pseudo_id,
                age_group=patient.age_group,
                gender=patient.gender,
                risk_score=None,
                risk_level=None,
                last_prediction_date=None
            ))
    
    # Get unique FHIR IDs from deid_patients
    existing_fhir_ids = {p.original_fhir_id for p in deid_patients if p.original_fhir_id}
    
    # Query fhir_patients table directly (patients not yet anonymized)
    from sqlalchemy import text
    fhir_query = text("""
        SELECT fhir_id, gender, birth_date, resource_data, created_at
        FROM fhir_patients
        WHERE active = true
        ORDER BY created_at DESC
        LIMIT :limit
    """)
    fhir_results = db.execute(fhir_query, {"limit": limit * 2}).fetchall()  # Get more to account for filtering
    
    for row in fhir_results:
        fhir_id = row[0]
        # Skip if already in deid_patients
        if fhir_id in existing_fhir_ids:
            continue
            
        gender = row[1]
        birth_date = row[2]
        resource_data = row[3] if row[3] else {}
        
        # Calculate age group if birth_date available
        age_group = None
        if birth_date:
            from datetime import datetime
            try:
                if isinstance(birth_date, str):
                    birth = datetime.strptime(birth_date[:10], '%Y-%m-%d')
                else:
                    birth = birth_date
                age = (datetime.now() - birth).days // 365
                if age < 18:
                    age_group = "0-17"
                elif age < 35:
                    age_group = "18-34"
                elif age < 50:
                    age_group = "35-49"
                elif age < 65:
                    age_group = "50-64"
                else:
                    age_group = "65+"
            except:
                pass
        
        result.append(PatientRiskSummary(
            patient_id=fhir_id,  # Use FHIR ID for non-anonymized patients
            age_group=age_group,
            gender=gender,
            risk_score=None,
            risk_level=None,
            last_prediction_date=None
        ))
    
    return result


@app.post("/api/v1/patients", response_model=PatientCreateResponse, tags=["Patients"])
async def create_patient(
    patient_data: PatientCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new patient in FHIR via ProxyFHIR service.
    Only admin and clinician can create patients.
    """
    # Check permissions
    if current_user.role not in ["admin", "clinician"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and clinician can create patients"
        )
    
    # Ensure resourceType is Patient
    patient_dict = patient_data.model_dump(exclude_none=True)
    patient_dict["resourceType"] = "Patient"
    
    # Forward request to ProxyFHIR service
    proxy_fhir_url = f"{settings.proxy_fhir_url}/api/fhir/proxy/Patient"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                proxy_fhir_url,
                json=patient_dict,
                headers={"Content-Type": "application/fhir+json"}
            )
            
            if response.status_code not in [200, 201]:
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail") or error_data.get("message") or response.text or "Failed to create patient in FHIR"
                except:
                    error_detail = response.text or "Failed to create patient in FHIR"
                
                logger.error(
                    "proxy_fhir_error",
                    status_code=response.status_code,
                    error=error_detail[:500]  # Truncate very long errors
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"ProxyFHIR service error: {error_detail[:500]}"
                )
            
            try:
                fhir_response = response.json()
            except Exception as e:
                logger.error("proxy_fhir_json_error", error=str(e), response_text=response.text[:200])
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Invalid JSON response from ProxyFHIR service"
                )
            
            # Return simplified response
            return PatientCreateResponse(
                id=fhir_response.get("id", ""),
                resourceType=fhir_response.get("resourceType", "Patient"),
                status="created"
            )
    
    except httpx.TimeoutException:
        logger.error("proxy_fhir_timeout", url=proxy_fhir_url)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="ProxyFHIR service timeout"
        )
    except httpx.RequestError as e:
        logger.error("proxy_fhir_request_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ProxyFHIR service unavailable: {str(e)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error("create_patient_error", error=error_msg, error_type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating patient: {error_msg}"
        )


@app.delete("/api/v1/patients/{patient_id}", tags=["Patients"])
async def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a patient (admin and clinician only).
    This will soft-delete the patient by setting active=false.
    """
    # Only admin and clinician can delete patients
    if current_user.role not in ["admin", "clinician"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and clinician can delete patients"
        )
    
    patient_service = PatientService(db)
    deleted = patient_service.delete_patient(patient_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    return {"message": f"Patient {patient_id} deleted successfully"}


@app.get("/api/v1/patients/high-risk", response_model=HighRiskPatientsResponse, tags=["Risk Scores"])
async def get_high_risk_patients(
    threshold: float = 0.7,
    service: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of high-risk patients above threshold.
    """
    risk_service = RiskScoreService(db)
    patients = risk_service.get_high_risk_patients(threshold, limit, service)
    
    return HighRiskPatientsResponse(
        threshold=threshold,
        count=len(patients),
        patients=[
            PatientRiskSummary(
                patient_id=p["patient_id"],
                age_group=p["age_group"],
                gender=p["gender"],
                risk_score=p["risk_score"],
                risk_level=p["risk_level"],
                last_prediction_date=p["last_prediction_date"]
            )
            for p in patients
        ]
    )


@app.post("/api/v1/patients/{patient_id}/predict", tags=["Risk Scores"])
async def request_new_prediction(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request a new risk prediction for a patient.
    """
    risk_service = RiskScoreService(db)
    result = await risk_service.request_prediction(patient_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate prediction"
        )
    
    return result


# ============================================
# Dashboard Endpoints
# ============================================

@app.get("/api/v1/dashboard/stats", response_model=DashboardStats, tags=["Dashboard"])
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics.
    """
    risk_service = RiskScoreService(db)
    return risk_service.get_dashboard_stats()


# ============================================
# User Management (Admin only)
# ============================================

@app.post("/api/v1/users", response_model=UserResponse, tags=["User Management"])
async def create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user (all authenticated users).
    """
    user_service = UserService(db)
    
    # Check if username exists
    if user_service.get_user_by_username(request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    if user_service.get_user_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    user = user_service.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        role=request.role,
        department=request.department
    )
    
    return user


@app.get("/api/v1/users", response_model=List[UserResponse], tags=["User Management"])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all users (all authenticated users).
    """
    user_service = UserService(db)
    return user_service.get_all_users()


# ============================================
# Audit Endpoints
# ============================================

@app.get("/api/v1/audit/logs", response_model=List[AuditLogEntry], tags=["Audit"])
async def get_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent audit logs (all authenticated users).
    """
    audit_service = AuditService(db)
    return audit_service.get_recent_logs(limit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.service_host, port=settings.service_port)

