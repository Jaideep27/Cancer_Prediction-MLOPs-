"""Gradient Boosting Classifier model implementation."""

from typing import Any, Dict, Optional

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier as SklearnGBC

from .base_model import BaseModel
from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GradientBoostingModel(BaseModel):
    """Gradient Boosting Classifier model."""

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialize Gradient Boosting model.

        Args:
            params: Model parameters
        """
        if params is None:
            model_config = get_config("model_config", "gradient_boosting.params")
            params = model_config if model_config else {}

        super().__init__(model_name="gradient_boosting", params=params)
        self.model = self.build()

    def build(self) -> SklearnGBC:
        """
        Build Gradient Boosting model.

        Returns:
            Scikit-learn GradientBoostingClassifier instance
        """
        logger.info(f"Building Gradient Boosting model with params: {self.params}")
        return SklearnGBC(**self.params)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GradientBoostingModel":
        """
        Train the Gradient Boosting model.

        Args:
            X: Training features
            y: Training labels

        Returns:
            Trained model instance
        """
        logger.info(f"Training Gradient Boosting on {len(X)} samples")
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("Gradient Boosting training complete")
        return self

    def get_feature_importance(self) -> np.ndarray:
        """
        Get feature importance scores.

        Returns:
            Feature importance array
        """
        if not self.is_trained:
            raise ValueError("Model must be trained to get feature importance")

        return self.model.feature_importances_
