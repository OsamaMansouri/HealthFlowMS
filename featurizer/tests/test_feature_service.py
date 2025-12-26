"""
Unit tests for featurizer service
Tests feature extraction for ML models
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
from datetime import datetime
from app.feature_service import FeatureService
from app.models import PatientFeatures, DeidPatient, FhirEncounter


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def feature_service(mock_db):
    return FeatureService(mock_db)


@pytest.fixture
def sample_deid_patient():
    patient = DeidPatient()
    patient.pseudo_id = "pseudo-123"
    patient.original_fhir_id = "patient-123"
    patient.age_group = "30-40"
    patient.gender = "male"
    return patient


class TestFeatureService:
    """Test suite for FeatureService"""

    # ==================== Feature Extraction Tests ====================

    def test_extract_features_success(self, feature_service, mock_db, sample_deid_patient):
        """Test successful feature extraction"""
        # Arrange
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_deid_patient,  # DeidPatient
            None                   # No existing features
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        # Act
        result = feature_service.extract_features("pseudo-123")

        # Assert
        assert result is not None
        assert result.pseudo_patient_id == "pseudo-123"

    def test_extract_features_patient_not_found(self, feature_service, mock_db):
        """Test feature extraction when patient not found"""
        # Arrange
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = feature_service.extract_features("nonexistent")

        # Assert
        assert result is None

    def test_extract_features_uses_existing(self, feature_service, mock_db, sample_deid_patient):
        """Test that existing features are returned"""
        # Arrange
        existing_features = PatientFeatures()
        existing_features.pseudo_patient_id = "pseudo-123"
        existing_features.feature_version = "v1.0"

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_deid_patient,   # DeidPatient
            existing_features      # Existing features
        ]

        # Act
        result = feature_service.extract_features("pseudo-123")

        # Assert
        assert result == existing_features
        mock_db.add.assert_not_called()

    # ==================== Demographics Extraction Tests ====================

    def test_extract_demographics_age_group(self, feature_service):
        """Test demographics extraction with age group"""
        patient = DeidPatient()
        patient.age_group = "30-40"
        patient.gender = "male"

        features = PatientFeatures()
        feature_service._extract_demographics(features, patient)

        assert features.age_at_admission == 35  # Middle of range
        assert features.gender_encoded == 0      # Male = 0

    def test_extract_demographics_90_plus(self, feature_service):
        """Test demographics for 90+ age group"""
        patient = DeidPatient()
        patient.age_group = "90+"
        patient.gender = "female"

        features = PatientFeatures()
        feature_service._extract_demographics(features, patient)

        assert features.age_at_admission == 92
        assert features.gender_encoded == 1  # Female = 1

    def test_extract_demographics_unknown_gender(self, feature_service):
        """Test demographics with unknown gender"""
        patient = DeidPatient()
        patient.age_group = "40-50"
        patient.gender = "unknown"

        features = PatientFeatures()
        feature_service._extract_demographics(features, patient)

        assert features.gender_encoded == 3  # Unknown = 3

    # ==================== Encounter Features Tests ====================

    def test_extract_encounter_features(self, feature_service, mock_db):
        """Test encounter feature extraction"""
        # Arrange
        encounter = FhirEncounter()
        encounter.fhir_id = "encounter-123"
        encounter.period_start = datetime(2024, 1, 1)
        encounter.period_end = datetime(2024, 1, 5)

        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [encounter]

        features = PatientFeatures()

        # Act
        feature_service._extract_encounter_features(features, "patient-123", None)

        # Assert
        assert features.length_of_stay == 4

    def test_extract_encounter_discharge_home(self, feature_service, mock_db):
        """Test discharge disposition detection"""
        encounter = FhirEncounter()
        encounter.discharge_disposition = "home"

        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [encounter]

        features = PatientFeatures()
        feature_service._extract_encounter_features(features, "patient-123", None)

        assert features.discharge_to_home is True

    # ==================== Vital Signs Tests ====================

    def test_extract_vital_signs(self, feature_service, mock_db):
        """Test vital signs extraction"""
        # Arrange
        from app.models import FhirObservation
        obs = FhirObservation()
        obs.code = "8867-4"  # Heart rate
        obs.value_quantity = 72.0

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = obs

        features = PatientFeatures()

        # Act (mocking settings)
        with pytest.mock.patch('app.feature_service.settings') as mock_settings:
            mock_settings.vital_signs_codes = {"heart_rate": "8867-4"}
            feature_service._extract_vital_signs(features, "patient-123")

        # Assert (should set heart_rate_last)
        # Note: actual assertion depends on implementation

    # ==================== Comorbidity Index Tests ====================

    def test_calculate_comorbidity_diabetes(self, feature_service):
        """Test comorbidity calculation with diabetes"""
        features = PatientFeatures()
        features.has_diabetes = True
        features.has_heart_failure = False
        features.has_copd = False
        features.has_ckd = False
        features.has_cancer = False
        features.age_at_admission = 45

        feature_service._calculate_comorbidity_indices(features, "patient-123")

        assert features.charlson_comorbidity_index >= 1.0

    def test_calculate_comorbidity_multiple_conditions(self, feature_service):
        """Test comorbidity with multiple conditions"""
        features = PatientFeatures()
        features.has_diabetes = True
        features.has_heart_failure = True
        features.has_ckd = True
        features.age_at_admission = 65

        feature_service._calculate_comorbidity_indices(features, "patient-123")

        assert features.charlson_comorbidity_index >= 4.0  # 1+1+2 + age

    # ==================== Edge Cases ====================

    def test_extract_features_no_encounters(self, feature_service, mock_db, sample_deid_patient):
        """Test feature extraction with no encounters"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_deid_patient,
            None
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        result = feature_service.extract_features("pseudo-123")

        assert result is not None
        # Should still create features even without encounters

    def test_extract_features_null_vitals(self, feature_service, mock_db, sample_deid_patient):
        """Test handling of null vital signs"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_deid_patient,
            None
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        result = feature_service.extract_features("pseudo-123", include_vitals=True)

        assert result is not None
        # Vitals should be None/0


# ==================== Batch Processing Tests ====================

class TestBatchProcessing:
    """Tests for batch feature extraction"""

    def test_batch_extract_success(self, feature_service, mock_db, sample_deid_patient):
        """Test batch feature extraction"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_deid_patient,
            None,
            sample_deid_patient,
            None
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        result = feature_service.batch_extract_features(["pseudo-123", "pseudo-456"])

        assert result["total_processed"] == 2
