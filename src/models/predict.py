"""Model prediction utilities."""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd

from .base_model import BaseModel
from .gradient_boosting import GradientBoostingModel
from .hybrid_ensemble import HybridEnsembleModel
from .logistic_regression import LogisticRegressionModel
from .neural_network import NeuralNetworkModel
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelPredictor:
    """Handles model predictions."""

    MODEL_REGISTRY = {
        "logistic_regression": LogisticRegressionModel,
        "gradient_boosting": GradientBoostingModel,
        "neural_network": NeuralNetworkModel,
        "hybrid_ensemble": HybridEnsembleModel,
    }

    def __init__(self, model: Optional[BaseModel] = None, model_path: Optional[str] = None):
        """
        Initialize predictor.

        Args:
            model: Pre-loaded model instance
            model_path: Path to load model from
        """
        self.model = model

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str) -> None:
        """
        Load model from disk.

        Args:
            model_path: Path to model directory
        """
        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(f"Model path not found: {model_path}")

        # Determine model type from path or metadata
        model_name = model_path.name

        if model_name not in self.MODEL_REGISTRY:
            logger.warning(f"Unknown model type: {model_name}, attempting to load anyway")
            # Try to infer from parent directory structure
            for registered_name in self.MODEL_REGISTRY:
                if registered_name in str(model_path):
                    model_name = registered_name
                    break

        model_class = self.MODEL_REGISTRY.get(model_name, LogisticRegressionModel)

        # Create model instance and load
        self.model = model_class()
        self.model.load(str(model_path))

        logger.info(f"Loaded model from {model_path}")

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Input features

        Returns:
            Predictions
        """
        if self.model is None:
            raise ValueError("No model loaded. Call load_model() first.")

        if isinstance(X, pd.DataFrame):
            X = X.values

        logger.info(f"Making predictions for {len(X)} samples")
        predictions = self.model.predict(X)

        return predictions

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Predict class probabilities.

        Args:
            X: Input features

        Returns:
            Class probabilities
        """
        if self.model is None:
            raise ValueError("No model loaded. Call load_model() first.")

        if isinstance(X, pd.DataFrame):
            X = X.values

        logger.info(f"Predicting probabilities for {len(X)} samples")
        probabilities = self.model.predict_proba(X)

        return probabilities

    def predict_with_confidence(
        self, X: Union[np.ndarray, pd.DataFrame], threshold: float = 0.5
    ) -> Dict[str, np.ndarray]:
        """
        Make predictions with confidence scores.

        Args:
            X: Input features
            threshold: Confidence threshold for predictions

        Returns:
            Dictionary with predictions, probabilities, and confidence
        """
        probabilities = self.predict_proba(X)

        # Get predicted class (binary classification)
        predictions = (probabilities[:, 1] >= threshold).astype(int)

        # Confidence is the max probability
        confidence = np.max(probabilities, axis=1)

        return {
            "predictions": predictions,
            "probabilities": probabilities,
            "confidence": confidence,
            "positive_proba": probabilities[:, 1],
        }

    def batch_predict(
        self, X: Union[np.ndarray, pd.DataFrame], batch_size: int = 32
    ) -> np.ndarray:
        """
        Make predictions in batches.

        Args:
            X: Input features
            batch_size: Batch size for predictions

        Returns:
            Predictions
        """
        if isinstance(X, pd.DataFrame):
            X = X.values

        n_samples = len(X)
        predictions = []

        logger.info(f"Batch prediction: {n_samples} samples, batch_size={batch_size}")

        for i in range(0, n_samples, batch_size):
            batch = X[i : i + batch_size]
            batch_pred = self.predict(batch)
            predictions.append(batch_pred)

        return np.concatenate(predictions)
