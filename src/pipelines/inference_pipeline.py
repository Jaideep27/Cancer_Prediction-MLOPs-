"""Inference pipeline for making predictions."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from ..features.build_features import FeatureBuilder
from ..models.predict import ModelPredictor
from ..models.registry import ModelRegistry
from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class InferencePipeline:
    """Complete inference pipeline for making predictions."""

    def __init__(
        self,
        model_name: str = "hybrid_ensemble",
        model_version: str = "latest",
        model_path: Optional[str] = None,
    ):
        """
        Initialize inference pipeline.

        Args:
            model_name: Name of model to use
            model_version: Version of model to use
            model_path: Optional direct path to model
        """
        self.model_name = model_name
        self.model_version = model_version

        # Initialize components
        self.feature_builder = FeatureBuilder()
        self.predictor = ModelPredictor()
        self.registry = ModelRegistry()

        # Load model
        if model_path:
            self.load_model_from_path(model_path)
        else:
            self.load_model_from_registry(model_name, model_version)

    def load_model_from_registry(self, model_name: str, version: str = "latest") -> None:
        """
        Load model from registry.

        Args:
            model_name: Name of the model
            version: Version identifier
        """
        logger.info(f"Loading model from registry: {model_name} v{version}")

        model_path = self.registry.get_model_path(model_name, version)

        if model_path is None:
            raise FileNotFoundError(
                f"Model not found in registry: {model_name} v{version}"
            )

        self.predictor.load_model(str(model_path))

        logger.info(f"Model loaded successfully from {model_path}")

    def load_model_from_path(self, model_path: str) -> None:
        """
        Load model from direct path.

        Args:
            model_path: Path to model directory
        """
        logger.info(f"Loading model from path: {model_path}")

        self.predictor.load_model(model_path)

        logger.info("Model loaded successfully")

    def prepare_input(
        self, data: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]]
    ) -> np.ndarray:
        """
        Prepare input data for prediction.

        Args:
            data: Input data in various formats

        Returns:
            Prepared feature array
        """
        # Convert to DataFrame if needed
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        elif isinstance(data, list):
            data = pd.DataFrame(data)
        elif isinstance(data, np.ndarray):
            # Assume it's already in the right format
            return data

        # Select features
        feature_names = self.feature_builder.get_feature_names()
        missing_features = [f for f in feature_names if f not in data.columns]

        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")

        # Extract features
        X = data[feature_names].values

        return X

    def predict(
        self,
        data: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]],
        return_proba: bool = False,
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        Make predictions.

        Args:
            data: Input data
            return_proba: Whether to return probabilities

        Returns:
            Predictions or dictionary with predictions and probabilities
        """
        logger.info("Making predictions")

        # Prepare input
        X = self.prepare_input(data)

        # Make predictions
        if return_proba:
            predictions = self.predictor.predict(X)
            probabilities = self.predictor.predict_proba(X)

            return {
                "predictions": predictions,
                "probabilities": probabilities,
                "positive_probability": probabilities[:, 1],
            }
        else:
            predictions = self.predictor.predict(X)
            return predictions

    def predict_with_confidence(
        self,
        data: Union[pd.DataFrame, np.ndarray, Dict[str, Any], List[Dict[str, Any]]],
        threshold: float = 0.5,
    ) -> Dict[str, np.ndarray]:
        """
        Make predictions with confidence scores.

        Args:
            data: Input data
            threshold: Confidence threshold

        Returns:
            Dictionary with predictions, probabilities, and confidence
        """
        logger.info("Making predictions with confidence")

        # Prepare input
        X = self.prepare_input(data)

        # Make predictions with confidence
        result = self.predictor.predict_with_confidence(X, threshold=threshold)

        return result

    def predict_single(
        self, features: Dict[str, float], return_proba: bool = True
    ) -> Dict[str, Any]:
        """
        Make prediction for a single instance.

        Args:
            features: Dictionary of feature values
            return_proba: Whether to return probabilities

        Returns:
            Prediction result
        """
        result = self.predict_with_confidence([features])

        output = {
            "prediction": int(result["predictions"][0]),
            "diagnosis": "Malignant" if result["predictions"][0] == 1 else "Benign",
            "confidence": float(result["confidence"][0]),
        }

        if return_proba:
            output["probability_benign"] = float(result["probabilities"][0][0])
            output["probability_malignant"] = float(result["probabilities"][0][1])

        return output

    def batch_predict(
        self,
        data: Union[pd.DataFrame, np.ndarray],
        batch_size: int = 32,
        return_proba: bool = False,
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        Make predictions in batches.

        Args:
            data: Input data
            batch_size: Batch size
            return_proba: Whether to return probabilities

        Returns:
            Predictions or dictionary with predictions and probabilities
        """
        logger.info(f"Batch prediction with batch_size={batch_size}")

        # Prepare input
        X = self.prepare_input(data)

        # Make batch predictions
        predictions = self.predictor.batch_predict(X, batch_size=batch_size)

        if return_proba:
            probabilities = self.predictor.predict_proba(X)
            return {
                "predictions": predictions,
                "probabilities": probabilities,
            }
        else:
            return predictions
