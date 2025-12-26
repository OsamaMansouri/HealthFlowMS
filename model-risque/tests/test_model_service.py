"""
Unit tests for model-risque service
Tests risk prediction and ML model functionality
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from app.model_service import ModelService, get_model
from app.models import RiskPrediction, PatientFeatures, MLModel


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def model_service(mock_db):
    return ModelService(mock_db)


@pytest.fixture
def sample_features():
    features = PatientFeatures()
    features.pseudo_patient_id = "pseudo-123"
    features.age_at_admission = 65
    features.gender_encoded = 0
    features.charlson_comorbidity_index = 3.0
    features.previous_admissions_30d = 1
    features.heart_rate_last = 80.0
    features.computed_at = datetime.now()
    return features


class TestModelService:
    """Test suite for ModelService"""

    # ==================== Prediction Tests ====================

    def test_predict_success(self, model_service, mock_db, sample_features):
        """Test successful risk prediction"""
        # Arrange
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.side_effect = [
            sample_features,  # Patient features
            None               # Active model
        ]

        with patch.object(model_service, 'model') as mock_model:
            mock_model.predict_proba.return_value = np.array([[0.3, 0.7]])

            # Act
            result = model_service.predict("pseudol-123")

            # Assert
            assert result is not None
            assert result.pseudo_patient_id == "pseudo-123"
            assert 0.0 <= result.risk_score <= 1.0
            assert result.risk_level in ["LOW", "MEDIUM", "HIGH"]

    def test_predict_features_not_found(self, model_service, mock_db):
        """Test prediction when features don't exist"""
        # Arrange
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        # Act
        result = model_service.predict("nonexistent")

        # Assert
        assert result is None

    def test_predict_high_risk(self, model_service, mock_db, sample_features):
        """Test high risk prediction"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.side_effect = [
            sample_features,
            None
        ]

        with patch.object(model_service, 'model') as mock_model:
            mock_model.predict_proba.return_value = np.array([[0.1, 0.9]])

            result = model_service.predict("pseudo-123")

            assert result.risk_level == "HIGH"
            assert result.risk_score >= 0.7

    def test_predict_low_risk(self, model_service, mock_db, sample_features):
        """Test low risk prediction"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.side_effect = [
            sample_features,
            None
        ]

        with patch.object(model_service, 'model') as mock_model:
            mock_model.predict_proba.return_value = np.array([[0.9, 0.1]])

            result = model_service.predict("pseudo-123")

            assert result.risk_level == "LOW"
            assert result.risk_score <= 0.3

    # ==================== Feature Preparation Tests ====================

    def test_get_features_for_patient(self, model_service, mock_db, sample_features):
        """Test feature retrieval for patient"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = sample_features

        features_dict = model_service.get_features_for_patient("pseudo-123")

        assert features_dict is not None
        assert "age_at_admission" in features_dict
        assert features_dict["age_at_admission"] == 65

    def test_prepare_features(self, model_service):
        """Test feature array preparation"""
        feature_dict = {
            "age_at_admission": 65,
            "gender_encoded": 0,
            "charlson_comorbidity_index": 3.0
        }

        features_array = model_service.prepare_features(feature_dict)

        assert isinstance(features_array, np.ndarray)
        assert features_array.shape[0] == 1

    # ==================== SHAP Explanations Tests ====================

    def test_calculate_shap_values(self, model_service):
        """Test SHAP value calculation"""
        features = np.array([[65, 0, 3.0, 1, 80.0, 120, 75, 18, 98, 6.0, 14.0, 1.2, 140, 4.0, 100, 12, 0.5, 0.3, 0.4, 5, 1, 0, 1, 0, 0, 0, 5, 2, 0]])

        with patch('app.model_service.get_shap_explainer') as mock_explainer:
            mock_shap = Mock()
            mock_shap.shap_values.return_value = np.random.randn(1, 29)
            mock_explainer.return_value = mock_shap

            top_factors, shap_values = model_service.calculate_shap_values(features)

            assert len(top_factors) <= 10
            assert len(shap_values) > 0

    # ==================== Risk Level Tests ====================

    def test_get_risk_level_high(self, model_service):
        """Test high risk level classification"""
        risk_level = model_service.get_risk_level(0.8)
        assert risk_level == "HIGH"

    def test_get_risk_level_medium(self, model_service):
        """Test medium risk level classification"""
        risk_level = model_service.get_risk_level(0.5)
        assert risk_level == "MEDIUM"

    def test_get_risk_level_low(self, model_service):
        """Test low risk level classification"""
        risk_level = model_service.get_risk_level(0.2)
        assert risk_level == "LOW"

    # ==================== Confidence Interval Tests ====================

    def test_calculate_confidence_interval(self, model_service):
        """Test confidence interval calculation"""
        lower, upper = model_service.calculate_confidence_interval(0.5)

        assert lower < 0.5 < upper
        assert 0.0 <= lower <= 1.0
        assert 0.0 <= upper <= 1.0

    # ==================== Batch Prediction Tests ====================

    def test_batch_predict(self, model_service, mock_db, sample_features):
        """Test batch prediction"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.side_effect = [
            sample_features,
            None,
            sample_features,
            None
        ]

        with patch.object(model_service, 'model') as mock_model:
            mock_model.predict_proba.return_value = np.array([[0.3, 0.7]])

            result = model_service.batch_predict(["pseudo-123", "pseudo-456"])

            assert result["total_processed"] == 2
            assert result["successful"] >= 0

    # ==================== Outcome Update Tests ====================

    def test_update_outcome_success(self, model_service, mock_db):
        """Test outcome update"""
        prediction = RiskPrediction()
        prediction.pseudo_patient_id = "pseudo-123"

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = prediction

        success = model_service.update_outcome("pseudo-123", True, datetime.now())

        assert success is True
        mock_db.commit.assert_called_once()

    def test_update_outcome_not_found(self, model_service, mock_db):
        """Test outcome update when prediction not found"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        success = model_service.update_outcome("nonexistent", True)

        assert success is False

    # ==================== Statistics Tests ====================

    def test_get_stats(self, model_service, mock_db):
        """Test statistics retrieval"""
        mock_db.query.return_value.scalar.return_value = 100

        stats = model_service.get_stats()

        assert "total_predictions" in stats
        assert "high_risk_count" in stats
        assert isinstance(stats["total_predictions"], int)


# ==================== Model Loading Tests ====================

class TestModelLoading:
    """Tests for ML model loading"""

    @patch('app.model_service._load_or_create_model')
    def test_get_model(self, mock_load):
        """Test model getter"""
        mock_model = Mock()
        mock_load.return_value = mock_model

        model = get_model()

        assert model == mock_model
        mock_load.assert_called_once()
