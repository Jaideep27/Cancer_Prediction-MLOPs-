"""Logistic Regression model implementation."""

from typing import Any, Dict, Optional

import numpy as np
from sklearn.linear_model import LogisticRegression as SklearnLR

from .base_model import BaseModel
from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LogisticRegressionModel(BaseModel):
    """Logistic Regression model."""

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialize Logistic Regression model.

        Args:
            params: Model parameters
        """
        if params is None:
            model_config = get_config("model_config", "logistic_regression.params")
            params = model_config if model_config else {}

        super().__init__(model_name="logistic_regression", params=params)
        self.model = self.build()

    def build(self) -> SklearnLR:
        """
        Build Logistic Regression model.

        Returns:
            Scikit-learn LogisticRegression instance
        """
        logger.info(f"Building Logistic Regression model with params: {self.params}")
        return SklearnLR(**self.params)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LogisticRegressionModel":
        """
        Train the Logistic Regression model.

        Args:
            X: Training features
            y: Training labels

        Returns:
            Trained model instance
        """
        logger.info(f"Training Logistic Regression on {len(X)} samples")
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("Logistic Regression training complete")
        return self
