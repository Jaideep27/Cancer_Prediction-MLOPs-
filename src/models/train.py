"""Model training orchestrator."""

from typing import Any, Dict, List, Optional, Union

import numpy as np

from .base_model import BaseModel
from .gradient_boosting import GradientBoostingModel
from .hybrid_ensemble import HybridEnsembleModel
from .logistic_regression import LogisticRegressionModel
from .neural_network import NeuralNetworkModel
from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelTrainer:
    """Orchestrates model training."""

    MODEL_REGISTRY = {
        "logistic_regression": LogisticRegressionModel,
        "gradient_boosting": GradientBoostingModel,
        "neural_network": NeuralNetworkModel,
        "hybrid_ensemble": HybridEnsembleModel,
    }

    def __init__(self):
        """Initialize model trainer."""
        self.trained_models: Dict[str, BaseModel] = {}

    def train_model(
        self,
        model_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        params: Optional[Dict[str, Any]] = None,
    ) -> BaseModel:
        """
        Train a single model.

        Args:
            model_name: Name of the model to train
            X_train: Training features
            y_train: Training labels
            params: Optional model parameters

        Returns:
            Trained model instance
        """
        if model_name not in self.MODEL_REGISTRY:
            raise ValueError(
                f"Unknown model: {model_name}. Available models: {list(self.MODEL_REGISTRY.keys())}"
            )

        logger.info(f"Training {model_name}...")

        # Special handling for ensemble model
        if model_name == "hybrid_ensemble":
            return self._train_ensemble(X_train, y_train, params)

        # Create and train model
        model_class = self.MODEL_REGISTRY[model_name]
        model = model_class(params=params)
        model.fit(X_train, y_train)

        # Store trained model
        self.trained_models[model_name] = model

        logger.info(f"{model_name} training complete")
        return model

    def _train_ensemble(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        params: Optional[Dict[str, Any]] = None,
    ) -> HybridEnsembleModel:
        """
        Train ensemble model with base models.

        Args:
            X_train: Training features
            y_train: Training labels
            params: Optional ensemble parameters

        Returns:
            Trained ensemble model
        """
        # Get ensemble configuration
        ensemble_config = get_config("model_config", "hybrid_ensemble")
        base_model_names = ensemble_config.get("models", [])

        if not base_model_names:
            base_model_names = ["logistic_regression", "gradient_boosting", "neural_network"]

        logger.info(f"Training base models for ensemble: {base_model_names}")

        # Train base models if not already trained
        base_models = []
        for model_name in base_model_names:
            if model_name in self.trained_models:
                logger.info(f"Using already trained {model_name}")
                base_models.append(self.trained_models[model_name])
            else:
                logger.info(f"Training {model_name} for ensemble")
                model = self.train_model(model_name, X_train, y_train)
                base_models.append(model)

        # Create and train ensemble
        ensemble = HybridEnsembleModel(base_models=base_models, params=params)
        ensemble.fit(X_train, y_train)

        # Store ensemble
        self.trained_models["hybrid_ensemble"] = ensemble

        logger.info("Hybrid Ensemble training complete")
        return ensemble

    def train_all_models(
        self, X_train: np.ndarray, y_train: np.ndarray, models_to_train: Optional[List[str]] = None
    ) -> Dict[str, BaseModel]:
        """
        Train multiple models.

        Args:
            X_train: Training features
            y_train: Training labels
            models_to_train: List of model names to train (default: all models)

        Returns:
            Dictionary of trained models
        """
        if models_to_train is None:
            training_config = get_config("training_config")
            models_to_train = training_config.get("models_to_train", list(self.MODEL_REGISTRY.keys()))

        logger.info(f"Training {len(models_to_train)} models: {models_to_train}")

        trained_models = {}

        for model_name in models_to_train:
            try:
                model = self.train_model(model_name, X_train, y_train)
                trained_models[model_name] = model
            except Exception as e:
                logger.error(f"Error training {model_name}: {str(e)}")
                raise

        logger.info(f"Successfully trained {len(trained_models)} models")
        return trained_models

    def get_trained_model(self, model_name: str) -> Optional[BaseModel]:
        """
        Get a trained model by name.

        Args:
            model_name: Name of the model

        Returns:
            Trained model or None if not found
        """
        return self.trained_models.get(model_name)

    def save_all_models(self, base_dir: str = "models") -> None:
        """
        Save all trained models.

        Args:
            base_dir: Base directory for saving models
        """
        from pathlib import Path

        for model_name, model in self.trained_models.items():
            save_dir = Path(base_dir) / model_name
            model.save(str(save_dir))
            logger.info(f"Saved {model_name} to {save_dir}")

        logger.info(f"All models saved to {base_dir}")
