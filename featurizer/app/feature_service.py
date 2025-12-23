"""Feature extraction service for patient data."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import structlog

from app.config import get_settings
from app.models import (
    PatientFeatures, NlpEntity, DeidPatient, 
    FhirEncounter, FhirObservation, FhirCondition, ClinicalNote
)
from app.nlp_service import nlp_service

settings = get_settings()
logger = structlog.get_logger()


class FeatureService:
    """Service for extracting patient features for ML models."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def extract_features(
        self, 
        pseudo_patient_id: str,
        encounter_id: Optional[str] = None,
        include_nlp: bool = True,
        include_vitals: bool = True,
        include_labs: bool = True
    ) -> Optional[PatientFeatures]:
        """Extract all features for a patient."""
        
        # Get de-identified patient
        deid_patient = self.db.query(DeidPatient).filter(
            DeidPatient.pseudo_id == pseudo_patient_id
        ).first()
        
        if not deid_patient:
            logger.warning("Patient not found", pseudo_id=pseudo_patient_id)
            return None
        
        # Check if features already exist
        existing = self.db.query(PatientFeatures).filter(
            PatientFeatures.pseudo_patient_id == pseudo_patient_id,
            PatientFeatures.encounter_id == encounter_id,
            PatientFeatures.feature_version == settings.feature_version
        ).first()
        
        if existing:
            logger.info("Using existing features", pseudo_id=pseudo_patient_id)
            return existing
        
        # Get original FHIR ID for lookups
        original_fhir_id = deid_patient.original_fhir_id
        
        # Create new features object
        features = PatientFeatures(
            pseudo_patient_id=pseudo_patient_id,
            encounter_id=encounter_id,
            feature_version=settings.feature_version
        )
        
        # Extract demographics
        self._extract_demographics(features, deid_patient)
        
        # Extract clinical features from encounters
        self._extract_encounter_features(features, original_fhir_id, encounter_id)
        
        # Extract vital signs
        if include_vitals:
            self._extract_vital_signs(features, original_fhir_id)
        
        # Extract lab values
        if include_labs:
            self._extract_lab_values(features, original_fhir_id)
        
        # Extract diagnosis features
        self._extract_diagnosis_features(features, original_fhir_id)
        
        # Extract NLP features
        if include_nlp:
            self._extract_nlp_features(features, original_fhir_id, pseudo_patient_id)
        
        # Calculate comorbidity indices
        self._calculate_comorbidity_indices(features, original_fhir_id)
        
        # Save features
        self.db.add(features)
        self.db.commit()
        self.db.refresh(features)
        
        logger.info("Features extracted successfully", 
                   pseudo_id=pseudo_patient_id,
                   feature_version=settings.feature_version)
        
        return features
    
    def _extract_demographics(self, features: PatientFeatures, deid_patient: DeidPatient):
        """Extract demographic features."""
        # Parse age from age_group
        age_group = deid_patient.age_group
        if age_group and "-" in age_group:
            try:
                min_age, max_age = age_group.split("-")
                features.age_at_admission = (int(min_age) + int(max_age)) // 2
            except ValueError:
                features.age_at_admission = None
        elif age_group == "90+":
            features.age_at_admission = 92
        
        # Encode gender
        gender = deid_patient.gender
        if gender:
            gender_map = {"male": 0, "female": 1, "other": 2, "unknown": 3}
            features.gender_encoded = gender_map.get(gender.lower(), 3)
    
    def _extract_encounter_features(
        self, 
        features: PatientFeatures, 
        patient_fhir_id: str,
        encounter_id: Optional[str]
    ):
        """Extract features from encounters."""
        # Get encounters
        encounters = self.db.query(FhirEncounter).filter(
            FhirEncounter.patient_fhir_id == patient_fhir_id
        ).order_by(FhirEncounter.period_start.desc()).all()
        
        if not encounters:
            return
        
        # Get the target encounter
        if encounter_id:
            target_encounter = next(
                (e for e in encounters if e.fhir_id == encounter_id), 
                encounters[0]
            )
        else:
            target_encounter = encounters[0]
        
        # Length of stay
        if target_encounter.period_start and target_encounter.period_end:
            los = target_encounter.period_end - target_encounter.period_start
            features.length_of_stay = los.days
        
        # Discharge disposition
        features.discharge_disposition = target_encounter.discharge_disposition
        features.discharge_to_home = (
            target_encounter.discharge_disposition and 
            "home" in target_encounter.discharge_disposition.lower()
        )
        
        # Count previous admissions
        if target_encounter.period_start:
            ref_date = target_encounter.period_start
            
            features.previous_admissions_30d = sum(
                1 for e in encounters 
                if e.period_end and e.period_end < ref_date 
                and (ref_date - e.period_end).days <= 30
            )
            
            features.previous_admissions_90d = sum(
                1 for e in encounters 
                if e.period_end and e.period_end < ref_date 
                and (ref_date - e.period_end).days <= 90
            )
            
            features.previous_admissions_365d = sum(
                1 for e in encounters 
                if e.period_end and e.period_end < ref_date 
                and (ref_date - e.period_end).days <= 365
            )
    
    def _extract_vital_signs(self, features: PatientFeatures, patient_fhir_id: str):
        """Extract vital signs features."""
        codes = settings.vital_signs_codes
        
        for feature_name, loinc_code in codes.items():
            obs = self.db.query(FhirObservation).filter(
                FhirObservation.patient_fhir_id == patient_fhir_id,
                FhirObservation.code == loinc_code
            ).order_by(FhirObservation.effective_date.desc()).first()
            
            if obs and obs.value_quantity:
                setattr(features, f"{feature_name}_last", float(obs.value_quantity))
    
    def _extract_lab_values(self, features: PatientFeatures, patient_fhir_id: str):
        """Extract lab value features."""
        codes = settings.lab_codes
        
        for feature_name, loinc_code in codes.items():
            obs = self.db.query(FhirObservation).filter(
                FhirObservation.patient_fhir_id == patient_fhir_id,
                FhirObservation.code == loinc_code
            ).order_by(FhirObservation.effective_date.desc()).first()
            
            if obs and obs.value_quantity:
                attr_name = f"{feature_name}_last"
                if feature_name == "wbc":
                    attr_name = "wbc_count_last"
                setattr(features, attr_name, float(obs.value_quantity))
    
    def _extract_diagnosis_features(self, features: PatientFeatures, patient_fhir_id: str):
        """Extract diagnosis-related features."""
        conditions = self.db.query(FhirCondition).filter(
            FhirCondition.patient_fhir_id == patient_fhir_id
        ).all()
        
        features.diagnosis_count = len(conditions)
        
        if conditions:
            features.primary_diagnosis_code = conditions[0].code
        
        # Check for specific comorbidities
        comorbidity_codes = settings.comorbidity_codes
        condition_codes = [c.code for c in conditions if c.code]
        
        for comorbidity, icd_prefixes in comorbidity_codes.items():
            has_condition = any(
                code.startswith(tuple(icd_prefixes)) 
                for code in condition_codes
            )
            setattr(features, f"has_{comorbidity}", has_condition)
    
    def _extract_nlp_features(
        self, 
        features: PatientFeatures, 
        patient_fhir_id: str,
        pseudo_patient_id: str
    ):
        """Extract NLP features from clinical notes."""
        notes = self.db.query(ClinicalNote).filter(
            ClinicalNote.patient_fhir_id == patient_fhir_id
        ).all()
        
        if not notes:
            return
        
        # Aggregate NLP scores across all notes
        all_sentiment = []
        all_urgency = []
        all_complexity = []
        total_entities = 0
        total_medications = 0
        total_symptoms = 0
        
        for note in notes:
            if not note.note_text:
                continue
            
            analysis = nlp_service.analyze_text(note.note_text)
            
            all_sentiment.append(analysis["sentiment_score"])
            all_urgency.append(analysis["urgency_score"])
            all_complexity.append(analysis["complexity_score"])
            total_entities += len(analysis["entities"])
            total_medications += analysis["medication_mentions"]
            total_symptoms += analysis["symptom_mentions"]
            
            # Save extracted entities
            for entity_data in analysis["entities"]:
                entity = NlpEntity(
                    pseudo_patient_id=pseudo_patient_id,
                    entity_type=entity_data["entity_type"],
                    entity_text=entity_data["entity_text"],
                    confidence=entity_data.get("confidence"),
                    start_position=entity_data.get("start_position"),
                    end_position=entity_data.get("end_position")
                )
                self.db.add(entity)
        
        # Calculate averages
        if all_sentiment:
            features.nlp_sentiment_score = sum(all_sentiment) / len(all_sentiment)
        if all_urgency:
            features.nlp_urgency_score = sum(all_urgency) / len(all_urgency)
        if all_complexity:
            features.nlp_complexity_score = sum(all_complexity) / len(all_complexity)
        
        features.nlp_entities_count = total_entities
        features.nlp_medication_mentions = total_medications
        features.nlp_symptom_mentions = total_symptoms
    
    def _calculate_comorbidity_indices(
        self, 
        features: PatientFeatures, 
        patient_fhir_id: str
    ):
        """Calculate Charlson Comorbidity Index."""
        # Simplified Charlson calculation based on available conditions
        score = 0
        
        if features.has_diabetes:
            score += 1
        if features.has_heart_failure:
            score += 1
        if features.has_copd:
            score += 1
        if features.has_ckd:
            score += 2
        if features.has_cancer:
            score += 2
        
        # Age adjustment
        if features.age_at_admission:
            if features.age_at_admission >= 50:
                score += (features.age_at_admission - 40) // 10
        
        features.charlson_comorbidity_index = float(score)
        
        # Simplified Elixhauser score (just sum of conditions)
        features.elixhauser_score = float(features.diagnosis_count or 0)
    
    def batch_extract_features(
        self,
        pseudo_patient_ids: List[str],
        include_nlp: bool = True,
        include_vitals: bool = True,
        include_labs: bool = True
    ) -> Dict[str, Any]:
        """Extract features for multiple patients."""
        results = []
        errors = []
        
        for pseudo_id in pseudo_patient_ids:
            try:
                features = self.extract_features(
                    pseudo_id,
                    include_nlp=include_nlp,
                    include_vitals=include_vitals,
                    include_labs=include_labs
                )
                
                if features:
                    results.append(features)
                else:
                    errors.append({
                        "pseudo_patient_id": pseudo_id,
                        "error": "Patient not found"
                    })
                    
            except Exception as e:
                logger.error("Error extracting features",
                           pseudo_id=pseudo_id, error=str(e))
                errors.append({
                    "pseudo_patient_id": pseudo_id,
                    "error": str(e)
                })
        
        return {
            "total_processed": len(pseudo_patient_ids),
            "successful": len(results),
            "failed": len(errors),
            "features": results,
            "errors": errors
        }
    
    def get_features_for_model(self, pseudo_patient_id: str) -> Optional[Dict[str, Any]]:
        """Get features formatted for ML model input."""
        features = self.db.query(PatientFeatures).filter(
            PatientFeatures.pseudo_patient_id == pseudo_patient_id,
            PatientFeatures.feature_version == settings.feature_version
        ).order_by(PatientFeatures.computed_at.desc()).first()
        
        if not features:
            return None
        
        # Convert to dict for model
        return {
            "age_at_admission": features.age_at_admission or 0,
            "gender_encoded": features.gender_encoded or 0,
            "length_of_stay": features.length_of_stay or 0,
            "previous_admissions_30d": features.previous_admissions_30d or 0,
            "previous_admissions_90d": features.previous_admissions_90d or 0,
            "previous_admissions_365d": features.previous_admissions_365d or 0,
            "charlson_comorbidity_index": features.charlson_comorbidity_index or 0,
            "heart_rate_last": features.heart_rate_last or 0,
            "blood_pressure_systolic_last": features.blood_pressure_systolic_last or 0,
            "blood_pressure_diastolic_last": features.blood_pressure_diastolic_last or 0,
            "respiratory_rate_last": features.respiratory_rate_last or 0,
            "temperature_last": features.temperature_last or 0,
            "oxygen_saturation_last": features.oxygen_saturation_last or 0,
            "hemoglobin_last": features.hemoglobin_last or 0,
            "creatinine_last": features.creatinine_last or 0,
            "sodium_last": features.sodium_last or 0,
            "potassium_last": features.potassium_last or 0,
            "glucose_last": features.glucose_last or 0,
            "wbc_count_last": features.wbc_count_last or 0,
            "nlp_sentiment_score": features.nlp_sentiment_score or 0.5,
            "nlp_urgency_score": features.nlp_urgency_score or 0.3,
            "nlp_complexity_score": features.nlp_complexity_score or 0.5,
            "diagnosis_count": features.diagnosis_count or 0,
            "has_diabetes": int(features.has_diabetes or False),
            "has_hypertension": int(features.has_hypertension or False),
            "has_heart_failure": int(features.has_heart_failure or False),
            "has_copd": int(features.has_copd or False),
            "has_ckd": int(features.has_ckd or False),
            "has_cancer": int(features.has_cancer or False),
            "medication_count": features.medication_count or 0,
            "procedure_count": features.procedure_count or 0,
            "discharge_to_home": int(features.discharge_to_home or False)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feature extraction statistics."""
        total_patients = self.db.query(
            func.count(func.distinct(PatientFeatures.pseudo_patient_id))
        ).scalar()
        
        total_features = self.db.query(func.count(PatientFeatures.id)).scalar()
        
        last_computed = self.db.query(PatientFeatures)\
            .order_by(PatientFeatures.computed_at.desc())\
            .first()
        
        return {
            "total_patients_processed": total_patients or 0,
            "total_features_computed": total_features or 0,
            "feature_version": settings.feature_version,
            "last_computed_at": last_computed.computed_at if last_computed else None
        }


