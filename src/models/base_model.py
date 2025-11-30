"""Base model class for all ML models."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from ..utils.helpers import save_pickle, load_pickle, save_json
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseModel(ABC):
    """Abstract base class for all models."""

    def __init__(self, model_name: str, params: Optional[Dict[str, Any]] = None):
        """
        Initialize base model.

        Args:
            model_name: Name of the model
            params: Model parameters
        """
        self.model_name = model_name
        self.params = params or {}
        self.model = None
        self.is_trained = False

    @abstractmethod
    def build(self) -> Any:
        """
        Build the model.

        Returns:
            Model instance
        """
        pass

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseModel":
        """
        Train the model.

        Args:
            X: Training features
            y: Training labels

        Returns:
            Trained model instance
        """
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Input features

        Returns:
            Predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.

        Args:
            X: Input features

        Returns:
            Class probabilities
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        else:
            raise NotImplementedError(
                f"Model {self.model_name} does not support probability predictions"
            )

    def save(self, save_dir: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Save model to disk.

        Args:
            save_dir: Directory to save model
            metadata: Optional metadata to save
        """
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        # Save model
        model_path = save_path / "model.pkl"
        save_pickle(self.model, str(model_path), compress=True)
        logger.info(f"Model saved to {model_path}")

        # Save metadata
        if metadata is None:
            metadata = {}

        metadata.update(
            {
                "model_name": self.model_name,
                "params": self.params,
                "is_trained": self.is_trained,
            }
        )

        metadata_path = save_path / "metadata.json"
        save_json(metadata, str(metadata_path))
        logger.info(f"Metadata saved to {metadata_path}")

    def load(self, load_dir: str) -> "BaseModel":
        """
        Load model from disk.

        Args:
            load_dir: Directory to load model from

        Returns:
            Loaded model instance
        """
        load_path = Path(load_dir)

        # Load model
        model_path = load_path / "model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        self.model = load_pickle(str(model_path))
        self.is_trained = True
        logger.info(f"Model loaded from {model_path}")

        return self

    def get_params(self) -> Dict[str, Any]:
        """
        Get model parameters.

        Returns:
            Model parameters
        """
        return self.params.copy()

    def set_params(self, **params: Any) -> "BaseModel":
        """
        Set model parameters.

        Args:
            **params: Parameters to set

        Returns:
            Model instance
        """
        self.params.update(params)
        return self
