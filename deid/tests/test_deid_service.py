"""
Unit tests for deid service
Tests anonymization, de-identification, and audit logging
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from app.deid_service import DeidService
from app.models import FhirPatient, DeidPatient, DeidAuditLog


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def deid_service(mock_db):
    """Create DeidService instance with mocked dependencies"""
    return DeidService(mock_db)


@pytest.fixture
def sample_patient():
    """Sample FHIR patient for testing"""
    patient = FhirPatient()
    patient.fhir_id = "patient-123"
    patient.gender = "male"
    patient.birth_date = "1990-01-01"
    patient.resource_data = {
        "id": "patient-123",
        "name": [{"family": "Doe", "given": ["John"]}],
        "telecom": [{"system": "phone", "value": "555-1234"}]
    }
    return patient


class TestDeidService:
    """Test suite for DeidService"""

    # ==================== Anonymization Tests ====================

    def test_anonymize_patient_success(self, deid_service, mock_db, sample_patient):
        """Test successful patient anonymization"""
        # Arrange
        mock_db.query.return_value.filter.return_value.first.return_value = sample_patient
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing deid

        # Act
        result = deid_service.anonymize_patient("patient-123")

        # Assert
        assert result is not None
        assert result.original_fhir_id == "patient-123"
        assert result.pseudo_id is not None
        assert len(result.pseudo_id) > 0

    def test_anonymize_patient_not_found(self, deid_service, mock_db):
        """Test anonymization when patient doesn't exist"""
        # Arrange
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = deid_service.anonymize_patient("nonexistent")

        # Assert
        assert result is None

    def test_anonymize_patient_already_anonymized(self, deid_service, mock_db, sample_patient):
        """Test re-anonymization of already anonymized patient"""
        # Arrange
        existing_deid = DeidPatient()
        existing_deid.pseudo_id = "pseudo-456"
        existing_deid.original_fhir_id = "patient-123"

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_patient,  # FhirPatient query
            existing_deid    # DeidPatient query
        ]

        # Act
        result = deid_service.anonymize_patient("patient-123")

        # Assert
        assert result == existing_deid
        assert result.pseudo_id == "pseudo-456"

    # ==================== Age Group Calculation Tests ====================

    def test_calculate_age_group_child(self, deid_service):
        """Test age group calculation for child"""
        birth_date = datetime(2015, 1, 1)
        age_group = deid_service.calculate_age_group(birth_date)
        assert "0-18" in age_group

    def test_calculate_age_group_adult(self, deid_service):
        """Test age group calculation for adult"""
        birth_date = datetime(1990, 1, 1)
        age_group = deid_service.calculate_age_group(birth_date)
        assert age_group in ["18-30", "30-40", "40-50"]

    def test_calculate_age_group_senior(self, deid_service):
        """Test age group calculation for senior"""
        birth_date = datetime(1940, 1, 1)
        age_group = deid_service.calculate_age_group(birth_date)
        assert age_group == "90+" or "70-90" in age_group

    def test_calculate_age_group_string_input(self, deid_service):
        """Test age group calculation with string date input"""
        birth_date = "1990-01-01"
        age_group = deid_service.calculate_age_group(birth_date)
        assert age_group is not None
        assert age_group != "unknown"

    def test_calculate_age_group_none(self, deid_service):
        """Test age group with None input"""
        age_group = deid_service.calculate_age_group(None)
        assert age_group == "unknown"

    # ==================== PII Removal Tests ====================

    def test_remove_pii_name(self, deid_service):
        """Test removal of name from patient data"""
        data = {
            "name": [{"family": "Doe", "given": ["John"]}],
            "id": "patient-123"
        }
        cleaned = deid_service.remove_pii(data)
        assert "name" not in cleaned

    def test_remove_pii_telecom(self, deid_service):
        """Test removal of telecom data"""
        data = {
            "telecom": [{"value": "555-1234"}],
            "id": "patient-123"
        }
        cleaned = deid_service.remove_pii(data)
        assert "telecom" not in cleaned

    def test_remove_pii_address(self, deid_service):
        """Test removal of address"""
        data = {
            "address": [{"line": ["123 Main St"], "city": "Springfield"}],
            "id": "patient-123"
        }
        cleaned = deid_service.remove_pii(data)
        assert "address" not in cleaned

    def test_remove_pii_preserves_id(self, deid_service):
        """Test that ID is preserved during PII removal"""
        data = {"id": "patient-123", "name": [{"family": "Doe"}]}
        cleaned = deid_service.remove_pii(data)
        assert "id" in cleaned
        assert cleaned["id"] == "patient-123"

    # ==================== Audit Logging Tests ====================

    def test_create_audit_log(self, deid_service, mock_db):
        """Test audit log creation"""
        # Act
        deid_service._create_audit_log(
            entity_type="Patient",
            original_id="patient-123",
            pseudo_id="pseudo-456",
            fields_modified=["name", "telecom"]
        )

        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    # ==================== Edge Cases ====================

    def test_anonymize_patient_empty_data(self, deid_service, mock_db):
        """Test anonymization with empty patient data"""
        patient = FhirPatient()
        patient.fhir_id = "patient-empty"
        patient.resource_data = {}

        mock_db.query.return_value.filter.return_value.first.side_effect = [patient, None]

        result = deid_service.anonymize_patient("patient-empty")
        assert result is not None

    def test_calculate_age_group_invalid_date(self, deid_service):
        """Test age group with  invalid date string"""
        age_group = deid_service.calculate_age_group("invalid-date")
        assert age_group == "unknown"


# ==================== Integration Tests ====================

class TestDeidServiceIntegration:
    """Integration tests for DeidService with real-like scenarios"""

    def test_full_anonymization_workflow(self, deid_service, mock_db, sample_patient):
        """Test complete anonymization workflow"""
        # Arrange
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_patient,  # Patient exists
            None             # Not yet anonymized
        ]

        # Act
        result = deid_service.anonymize_patient("patient-123")

        # Assert
        assert result is not None
        assert result.pseudo_id != sample_patient.fhir_id
        assert result.age_group is not None
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
