"""Neural Network (MLP) model implementation."""

from typing import Any, Dict, Optional

import numpy as np
from sklearn.neural_network import MLPClassifier as SklearnMLP

from .base_model import BaseModel
from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NeuralNetworkModel(BaseModel):
    """Multi-layer Perceptron (Neural Network) model."""

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialize Neural Network model.

        Args:
            params: Model parameters
        """
        if params is None:
            model_config = get_config("model_config", "neural_network.params")
            params = model_config if model_config else {}

        # Convert list to tuple for hidden_layer_sizes if needed
        if "hidden_layer_sizes" in params and isinstance(params["hidden_layer_sizes"], list):
            params["hidden_layer_sizes"] = tuple(params["hidden_layer_sizes"])

        super().__init__(model_name="neural_network", params=params)
        self.model = self.build()

    def build(self) -> SklearnMLP:
        """
        Build Neural Network model.

        Returns:
            Scikit-learn MLPClassifier instance
        """
        logger.info(f"Building Neural Network model with params: {self.params}")
        return SklearnMLP(**self.params)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NeuralNetworkModel":
        """
        Train the Neural Network model.

        Args:
            X: Training features
            y: Training labels

        Returns:
            Trained model instance
        """
        logger.info(f"Training Neural Network on {len(X)} samples")
        self.model.fit(X, y)
        self.is_trained = True
        logger.info(f"Neural Network training complete (iterations: {self.model.n_iter_})")
        return self

    def get_training_loss(self) -> list:
        """
        Get training loss curve.

        Returns:
            List of loss values during training
        """
        if not self.is_trained:
            raise ValueError("Model must be trained to get training loss")

        return self.model.loss_curve_
