"""Hybrid Ensemble model implementation."""

from typing import Any, Dict, List, Optional

import numpy as np
from mlxtend.classifier import EnsembleVoteClassifier

from .base_model import BaseModel
from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class HybridEnsembleModel(BaseModel):
    """Hybrid Ensemble model combining multiple classifiers."""

    def __init__(
        self,
        base_models: Optional[List[BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Hybrid Ensemble model.

        Args:
            base_models: List of trained base models
            params: Model parameters (voting, weights)
        """
        if params is None:
            model_config = get_config("model_config", "hybrid_ensemble.params")
            params = model_config if model_config else {}

        super().__init__(model_name="hybrid_ensemble", params=params)
        self.base_models = base_models or []
        self.model = None

    def set_base_models(self, base_models: List[BaseModel]) -> "HybridEnsembleModel":
        """
        Set base models for the ensemble.

        Args:
            base_models: List of trained base models

        Returns:
            Ensemble model instance
        """
        self.base_models = base_models
        logger.info(f"Set {len(base_models)} base models for ensemble")
        return self

    def build(self) -> EnsembleVoteClassifier:
        """
        Build Ensemble model from base models.

        Returns:
            mlxtend EnsembleVoteClassifier instance
        """
        if not self.base_models:
            raise ValueError("Base models must be set before building ensemble")

        # Extract sklearn models from BaseModel instances
        clfs = [model.model for model in self.base_models]

        logger.info(
            f"Building Hybrid Ensemble with {len(clfs)} models and params: {self.params}"
        )

        return EnsembleVoteClassifier(clfs=clfs, **self.params)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "HybridEnsembleModel":
        """
        Train the Ensemble model.

        Note: Base models should already be trained. This method fits the ensemble.

        Args:
            X: Training features
            y: Training labels

        Returns:
            Trained ensemble model instance
        """
        if not self.base_models:
            raise ValueError("Base models must be set and trained before fitting ensemble")

        # Build ensemble if not already built
        if self.model is None:
            self.model = self.build()

        logger.info(f"Fitting Hybrid Ensemble on {len(X)} samples")
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("Hybrid Ensemble training complete")
        return self

    def get_base_model_names(self) -> List[str]:
        """
        Get names of base models.

        Returns:
            List of base model names
        """
        return [model.model_name for model in self.base_models]
