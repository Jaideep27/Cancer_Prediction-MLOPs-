"""Unit tests for models."""

import numpy as np
import pytest

from src.models.logistic_regression import LogisticRegressionModel
from src.models.gradient_boosting import GradientBoostingModel
from src.models.neural_network import NeuralNetworkModel
from src.models.evaluate import ModelEvaluator


class TestLogisticRegressionModel:
    """Tests for Logistic Regression model."""

    def test_build(self):
        """Test model building."""
        model = LogisticRegressionModel()

        assert model.model is not None
        assert model.model_name == "logistic_regression"

    def test_fit_predict(self, sample_X_y):
        """Test model training and prediction."""
        X, y = sample_X_y
        model = LogisticRegressionModel()

        # Train
        model.fit(X, y)
        assert model.is_trained is True

        # Predict
        predictions = model.predict(X)
        assert len(predictions) == len(y)
        assert all(p in [0, 1] for p in predictions)

    def test_predict_proba(self, sample_X_y):
        """Test probability predictions."""
        X, y = sample_X_y
        model = LogisticRegressionModel()

        model.fit(X, y)
        probas = model.predict_proba(X)

        assert probas.shape == (len(X), 2)
        assert np.allclose(probas.sum(axis=1), 1.0)

    def test_save_load(self, sample_X_y, tmp_model_dir):
        """Test model saving and loading."""
        X, y = sample_X_y
        model = LogisticRegressionModel()
        model.fit(X, y)

        # Save
        model.save(str(tmp_model_dir))

        # Load
        loaded_model = LogisticRegressionModel()
        loaded_model.load(str(tmp_model_dir))

        assert loaded_model.is_trained is True

        # Compare predictions
        orig_pred = model.predict(X[:10])
        loaded_pred = loaded_model.predict(X[:10])

        assert np.array_equal(orig_pred, loaded_pred)


class TestGradientBoostingModel:
    """Tests for Gradient Boosting model."""

    def test_build(self):
        """Test model building."""
        model = GradientBoostingModel()

        assert model.model is not None
        assert model.model_name == "gradient_boosting"

    def test_fit_predict(self, sample_X_y):
        """Test model training and prediction."""
        X, y = sample_X_y
        model = GradientBoostingModel()

        model.fit(X, y)
        predictions = model.predict(X)

        assert len(predictions) == len(y)
        assert model.is_trained is True

    def test_feature_importance(self, sample_X_y):
        """Test feature importance extraction."""
        X, y = sample_X_y
        model = GradientBoostingModel()

        model.fit(X, y)
        importance = model.get_feature_importance()

        assert len(importance) == X.shape[1]
        assert all(imp >= 0 for imp in importance)


class TestNeuralNetworkModel:
    """Tests for Neural Network model."""

    def test_build(self):
        """Test model building."""
        params = {
            "hidden_layer_sizes": (10, 10),
            "max_iter": 100,
            "random_state": 42,
        }
        model = NeuralNetworkModel(params=params)

        assert model.model is not None
        assert model.model_name == "neural_network"

    def test_fit_predict(self, sample_X_y):
        """Test model training and prediction."""
        X, y = sample_X_y
        params = {
            "hidden_layer_sizes": (10, 10),
            "max_iter": 100,
            "random_state": 42,
        }
        model = NeuralNetworkModel(params=params)

        model.fit(X, y)
        predictions = model.predict(X)

        assert len(predictions) == len(y)
        assert model.is_trained is True


class TestModelEvaluator:
    """Tests for Model Evaluator."""

    def test_evaluate(self, sample_X_y):
        """Test model evaluation."""
        X, y = sample_X_y
        model = LogisticRegressionModel()
        model.fit(X, y)

        evaluator = ModelEvaluator(model)
        metrics = evaluator.evaluate(X, y)

        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "confusion_matrix" in metrics

    def test_calculate_metrics(self):
        """Test metric calculation."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])

        evaluator = ModelEvaluator()
        metrics = evaluator.calculate_metrics(y_true, y_pred)

        assert metrics["accuracy"] == 0.8
        assert "precision" in metrics
        assert "recall" in metrics
