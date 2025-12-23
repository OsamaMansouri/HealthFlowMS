"""Service layer for ScoreAPI."""
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx
import structlog

from app.config import get_settings
from app.models import User, ApiAuditLog, RiskPrediction, DeidPatient
from app.auth import get_password_hash

settings = get_settings()
logger = structlog.get_logger()


class UserService:
    """Service for user management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: str = "clinician",
        department: Optional[str] = None
    ) -> User:
        """Create a new user."""
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
            role=role,
            department=department
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_last_login(self, user: User):
        """Update user's last login timestamp."""
        user.last_login = datetime.now()
        self.db.commit()
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        return self.db.query(User).all()
    
    def update_user(self, user: User, updates: Dict[str, Any]) -> User:
        """Update user fields."""
        for key, value in updates.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user


class AuditService:
    """Service for audit logging."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_request(
        self,
        user_id: Optional[str],
        endpoint: str,
        method: str,
        request_params: Optional[Dict] = None,
        response_status: Optional[int] = None,
        patient_ids: Optional[List[str]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ):
        """Log an API request."""
        log_entry = ApiAuditLog(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            request_params=request_params,
            response_status=response_status,
            patient_ids_accessed=patient_ids,
            ip_address=ip_address,
            user_agent=user_agent,
            response_time_ms=response_time_ms
        )
        self.db.add(log_entry)
        self.db.commit()
    
    def get_recent_logs(self, limit: int = 100) -> List[ApiAuditLog]:
        """Get recent audit logs."""
        return self.db.query(ApiAuditLog)\
            .order_by(ApiAuditLog.request_timestamp.desc())\
            .limit(limit)\
            .all()
    
    def get_logs_for_user(self, user_id: str, limit: int = 100) -> List[ApiAuditLog]:
        """Get audit logs for a specific user."""
        return self.db.query(ApiAuditLog)\
            .filter(ApiAuditLog.user_id == user_id)\
            .order_by(ApiAuditLog.request_timestamp.desc())\
            .limit(limit)\
            .all()


class RiskScoreService:
    """Service for risk score operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_patient_risk_score(self, patient_id: str) -> Optional[RiskPrediction]:
        """Get latest risk score for a patient."""
        return self.db.query(RiskPrediction)\
            .filter(RiskPrediction.pseudo_patient_id == patient_id)\
            .order_by(RiskPrediction.prediction_timestamp.desc())\
            .first()
    
    def get_high_risk_patients(
        self, 
        threshold: float = 0.7, 
        limit: int = 100,
        service: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get high risk patients."""
        query = self.db.query(
            RiskPrediction.pseudo_patient_id,
            RiskPrediction.risk_score,
            RiskPrediction.risk_level,
            RiskPrediction.prediction_timestamp,
            DeidPatient.age_group,
            DeidPatient.gender
        ).outerjoin(
            DeidPatient,
            RiskPrediction.pseudo_patient_id == DeidPatient.pseudo_id
        ).filter(
            RiskPrediction.risk_score >= threshold
        ).order_by(
            RiskPrediction.risk_score.desc()
        ).limit(limit)
        
        results = query.all()
        
        return [
            {
                "patient_id": r.pseudo_patient_id,
                "risk_score": r.risk_score,
                "risk_level": r.risk_level,
                "last_prediction_date": r.prediction_timestamp,
                "age_group": r.age_group,
                "gender": r.gender
            }
            for r in results
        ]
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        total_patients = self.db.query(
            func.count(func.distinct(DeidPatient.pseudo_id))
        ).scalar() or 0
        
        high_risk = self.db.query(func.count(RiskPrediction.id)).filter(
            RiskPrediction.risk_level == "HIGH"
        ).scalar() or 0
        
        medium_risk = self.db.query(func.count(RiskPrediction.id)).filter(
            RiskPrediction.risk_level == "MEDIUM"
        ).scalar() or 0
        
        low_risk = self.db.query(func.count(RiskPrediction.id)).filter(
            RiskPrediction.risk_level == "LOW"
        ).scalar() or 0
        
        today = date.today()
        predictions_today = self.db.query(func.count(RiskPrediction.id)).filter(
            func.date(RiskPrediction.prediction_timestamp) == today
        ).scalar() or 0
        
        avg_score = self.db.query(func.avg(RiskPrediction.risk_score)).scalar()
        
        return {
            "total_patients": total_patients,
            "high_risk_patients": high_risk,
            "medium_risk_patients": medium_risk,
            "low_risk_patients": low_risk,
            "predictions_today": predictions_today,
            "average_risk_score": float(avg_score) if avg_score else 0,
            "model_accuracy": 0.82  # From model training metrics
        }
    
    async def request_prediction(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Request a new prediction from the model service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.model_service_url}/api/predict",
                    json={"pseudo_patient_id": patient_id},
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        "Prediction request failed",
                        status=response.status_code,
                        patient_id=patient_id
                    )
                    return None
        except Exception as e:
            logger.error("Error requesting prediction", error=str(e))
            return None


class PatientService:
    """Service for patient operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_patient(self, patient_id: str) -> Optional[DeidPatient]:
        """Get de-identified patient by pseudo ID."""
        return self.db.query(DeidPatient).filter(
            DeidPatient.pseudo_id == patient_id
        ).first()
    
    def search_patients(
        self, 
        age_group: Optional[str] = None,
        gender: Optional[str] = None,
        limit: int = 100
    ) -> List[DeidPatient]:
        """Search patients with filters."""
        query = self.db.query(DeidPatient)
        
        if age_group:
            query = query.filter(DeidPatient.age_group == age_group)
        if gender:
            query = query.filter(DeidPatient.gender == gender)
        
        return query.limit(limit).all()
    
    def get_patient_summary(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient summary with risk information."""
        patient = self.get_patient(patient_id)
        if not patient:
            return None
        
        # Get latest risk prediction
        prediction = self.db.query(RiskPrediction).filter(
            RiskPrediction.pseudo_patient_id == patient_id
        ).order_by(RiskPrediction.prediction_timestamp.desc()).first()
        
        return {
            "patient_id": patient.pseudo_id,
            "age_group": patient.age_group,
            "gender": patient.gender,
            "risk_score": prediction.risk_score if prediction else None,
            "risk_level": prediction.risk_level if prediction else None,
            "last_prediction_date": prediction.prediction_timestamp if prediction else None
        }
    
    def delete_patient(self, patient_id: str) -> bool:
        """Delete a patient by FHIR ID or pseudo ID. Returns True if deleted."""
        from sqlalchemy import text
        
        # First, try to find in deid_patients by pseudo_id
        deid_patient = self.db.query(DeidPatient).filter(
            DeidPatient.pseudo_id == patient_id
        ).first()
        
        if deid_patient:
            # Delete from deid_patients
            original_fhir_id = deid_patient.original_fhir_id
            self.db.delete(deid_patient)
            
            # Also delete from fhir_patients if exists
            fhir_query = text("""
                UPDATE fhir_patients 
                SET active = false 
                WHERE fhir_id = :fhir_id
            """)
            self.db.execute(fhir_query, {"fhir_id": original_fhir_id})
            
            # Delete related risk predictions
            self.db.query(RiskPrediction).filter(
                RiskPrediction.pseudo_patient_id == patient_id
            ).delete()
            
            self.db.commit()
            return True
        
        # If not in deid_patients, try to delete from fhir_patients directly
        fhir_query = text("""
            UPDATE fhir_patients 
            SET active = false 
            WHERE fhir_id = :fhir_id
        """)
        result = self.db.execute(fhir_query, {"fhir_id": patient_id})
        self.db.commit()
        
        return result.rowcount > 0


