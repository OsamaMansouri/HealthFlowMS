"""De-identification service logic."""
import hashlib
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from faker import Faker
from sqlalchemy.orm import Session
import structlog

from app.config import get_settings
from app.models import DeidPatient, DeidAuditLog, FhirPatient

settings = get_settings()
logger = structlog.get_logger()
fake = Faker()

# Fields to completely remove (direct identifiers)
FIELDS_TO_REMOVE = [
    "name", "telecom", "address", "photo", "contact",
    "identifier", "managingOrganization", "generalPractitioner",
    "link", "text"
]

# Fields to modify/generalize
FIELDS_TO_MODIFY = [
    "birthDate", "deceasedDateTime", "multipleBirth"
]


class DeIdentificationService:
    """Service for de-identifying patient data according to HIPAA Safe Harbor."""
    
    def __init__(self, db: Session):
        self.db = db
        self.salt = settings.deid_salt
        
    def generate_pseudo_id(self, original_id: str) -> str:
        """Generate a consistent pseudo identifier using salted hash."""
        combined = f"{self.salt}:{original_id}"
        hash_object = hashlib.sha256(combined.encode())
        return f"DEID-{hash_object.hexdigest()[:16].upper()}"
    
    def calculate_age_group(self, birth_date: datetime) -> str:
        """Calculate age group from birth date."""
        if not birth_date:
            return "unknown"
        
        today = datetime.now()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
        
        # Age groups as per configuration
        bins = settings.age_group_bins
        for i in range(len(bins) - 1):
            if bins[i] <= age < bins[i + 1]:
                return f"{bins[i]}-{bins[i + 1]}"
        
        return "90+"
    
    def shift_date(self, original_date: datetime, patient_seed: str) -> datetime:
        """Shift date by a consistent random amount based on patient."""
        if not original_date:
            return None
        
        # Use patient seed for consistent shifting
        random.seed(f"{self.salt}:{patient_seed}")
        shift_days = random.randint(-settings.date_shift_range_days, 
                                    settings.date_shift_range_days)
        return original_date + timedelta(days=shift_days)
    
    def deidentify_patient(self, patient_fhir_id: str) -> Tuple[Optional[DeidPatient], List[str], List[str]]:
        """
        De-identify a patient by FHIR ID.
        
        Returns:
            Tuple of (DeidPatient, removed_fields, modified_fields)
        """
        # Check if already de-identified
        existing = self.db.query(DeidPatient).filter(
            DeidPatient.original_fhir_id == patient_fhir_id
        ).first()
        
        if existing:
            logger.info("Patient already de-identified", 
                       original_id=patient_fhir_id, 
                       pseudo_id=existing.pseudo_id)
            return existing, [], []
        
        # Fetch original patient data
        fhir_patient = self.db.query(FhirPatient).filter(
            FhirPatient.fhir_id == patient_fhir_id
        ).first()
        
        if not fhir_patient:
            logger.warning("Patient not found", patient_id=patient_fhir_id)
            return None, [], []
        
        # Generate pseudo ID
        pseudo_id = self.generate_pseudo_id(patient_fhir_id)
        
        # Get original resource data
        resource_data = dict(fhir_patient.resource_data) if fhir_patient.resource_data else {}
        
        # Track modifications
        removed_fields = []
        modified_fields = []
        
        # Remove direct identifiers
        deid_data = {}
        for key, value in resource_data.items():
            if key in FIELDS_TO_REMOVE:
                removed_fields.append(key)
            else:
                deid_data[key] = value
        
        # Modify/generalize fields
        birth_date = fhir_patient.birth_date
        age_group = self.calculate_age_group(birth_date) if birth_date else "unknown"
        
        if "birthDate" in deid_data:
            # Replace exact birth date with year only (if age > 89, use 90+)
            if birth_date:
                year = birth_date.year
                age = datetime.now().year - year
                if age > 89:
                    deid_data["birthDate"] = "1900-01-01"  # Mask for 90+
                else:
                    deid_data["birthDate"] = f"{year}-01-01"  # Keep year only
                modified_fields.append("birthDate")
        
        # Replace ID with pseudo ID
        deid_data["id"] = pseudo_id
        modified_fields.append("id")
        
        # Add de-identification metadata
        deid_data["meta"] = {
            "deidentified": True,
            "deidentification_method": "safe_harbor",
            "deidentification_date": datetime.now().isoformat()
        }
        
        # Create de-identified patient record
        deid_patient = DeidPatient(
            original_fhir_id=patient_fhir_id,
            pseudo_id=pseudo_id,
            deid_data=deid_data,
            age_group=age_group,
            gender=fhir_patient.gender
        )
        
        self.db.add(deid_patient)
        
        # Log the operation
        audit_log = DeidAuditLog(
            operation="deidentify",
            entity_type="Patient",
            original_id=patient_fhir_id,
            pseudo_id=pseudo_id,
            fields_modified={
                "removed": removed_fields,
                "modified": modified_fields
            }
        )
        self.db.add(audit_log)
        
        self.db.commit()
        self.db.refresh(deid_patient)
        
        logger.info("Patient de-identified successfully",
                   original_id=patient_fhir_id,
                   pseudo_id=pseudo_id,
                   removed_fields=len(removed_fields),
                   modified_fields=len(modified_fields))
        
        return deid_patient, removed_fields, modified_fields
    
    def batch_deidentify(self, patient_fhir_ids: List[str]) -> Dict[str, Any]:
        """De-identify multiple patients."""
        results = []
        errors = []
        
        for patient_id in patient_fhir_ids:
            try:
                deid_patient, removed, modified = self.deidentify_patient(patient_id)
                if deid_patient:
                    results.append({
                        "pseudo_id": deid_patient.pseudo_id,
                        "age_group": deid_patient.age_group,
                        "gender": deid_patient.gender,
                        "deid_data": deid_patient.deid_data,
                        "fields_removed": removed,
                        "fields_modified": modified,
                        "deid_timestamp": deid_patient.deid_timestamp
                    })
                else:
                    errors.append({
                        "patient_id": patient_id,
                        "error": "Patient not found"
                    })
            except Exception as e:
                logger.error("Error de-identifying patient", 
                            patient_id=patient_id, error=str(e))
                errors.append({
                    "patient_id": patient_id,
                    "error": str(e)
                })
        
        return {
            "total_processed": len(patient_fhir_ids),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
    
    def get_pseudo_mapping(self, original_id: str) -> Optional[DeidPatient]:
        """Get pseudo ID mapping for an original patient ID."""
        return self.db.query(DeidPatient).filter(
            DeidPatient.original_fhir_id == original_id
        ).first()
    
    def get_by_pseudo_id(self, pseudo_id: str) -> Optional[DeidPatient]:
        """Get de-identified patient by pseudo ID."""
        return self.db.query(DeidPatient).filter(
            DeidPatient.pseudo_id == pseudo_id
        ).first()
    
    def get_audit_log(self, limit: int = 100) -> List[DeidAuditLog]:
        """Get recent audit log entries."""
        return self.db.query(DeidAuditLog)\
            .order_by(DeidAuditLog.performed_at.desc())\
            .limit(limit)\
            .all()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get de-identification statistics."""
        from sqlalchemy import func
        from datetime import date
        
        total_patients = self.db.query(func.count(DeidPatient.id)).scalar()
        total_operations = self.db.query(func.count(DeidAuditLog.id)).scalar()
        
        today = date.today()
        operations_today = self.db.query(func.count(DeidAuditLog.id))\
            .filter(func.date(DeidAuditLog.performed_at) == today)\
            .scalar()
        
        last_operation = self.db.query(DeidAuditLog)\
            .order_by(DeidAuditLog.performed_at.desc())\
            .first()
        
        return {
            "total_patients_deid": total_patients,
            "total_operations": total_operations,
            "operations_today": operations_today,
            "last_operation_at": last_operation.performed_at if last_operation else None
        }
    
    def delete_patient_data(self, original_id: str) -> bool:
        """
        Delete all de-identified data for a patient (right to erasure).
        """
        deid_patient = self.db.query(DeidPatient).filter(
            DeidPatient.original_fhir_id == original_id
        ).first()
        
        if not deid_patient:
            return False
        
        pseudo_id = deid_patient.pseudo_id
        
        # Log deletion
        audit_log = DeidAuditLog(
            operation="delete",
            entity_type="Patient",
            original_id=original_id,
            pseudo_id=pseudo_id,
            fields_modified={"reason": "right_to_erasure"}
        )
        self.db.add(audit_log)
        
        # Delete the record
        self.db.delete(deid_patient)
        self.db.commit()
        
        logger.info("Patient data deleted", 
                   original_id=original_id, 
                   pseudo_id=pseudo_id)
        
        return True


