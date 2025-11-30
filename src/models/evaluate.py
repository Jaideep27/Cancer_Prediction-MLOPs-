"""Model evaluation utilities."""

from typing import Any, Dict, Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from .base_model import BaseModel
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelEvaluator:
    """Evaluates model performance."""

    def __init__(self, model: Optional[BaseModel] = None):
        """
        Initialize evaluator.

        Args:
            model: Model to evaluate
        """
        self.model = model

    def set_model(self, model: BaseModel) -> None:
        """
        Set model to evaluate.

        Args:
            model: Model instance
        """
        self.model = model

    def evaluate(
        self, X: np.ndarray, y_true: np.ndarray, return_predictions: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate model performance.

        Args:
            X: Input features
            y_true: True labels
            return_predictions: Whether to return predictions

        Returns:
            Dictionary with evaluation metrics
        """
        if self.model is None:
            raise ValueError("No model set. Call set_model() first.")

        logger.info(f"Evaluating model on {len(X)} samples")

        # Make predictions
        y_pred = self.model.predict(X)
        y_proba = self.model.predict_proba(X) if hasattr(self.model, "predict_proba") else None

        # Calculate metrics
        metrics = self.calculate_metrics(y_true, y_pred, y_proba)

        if return_predictions:
            metrics["predictions"] = y_pred
            if y_proba is not None:
                metrics["probabilities"] = y_proba

        return metrics

    def calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Calculate evaluation metrics.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional)

        Returns:
            Dictionary of metrics
        """
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average="binary")),
            "recall": float(recall_score(y_true, y_pred, average="binary")),
            "f1_score": float(f1_score(y_true, y_pred, average="binary")),
        }

        # Add ROC AUC if probabilities available
        if y_proba is not None:
            # Use probability of positive class
            if y_proba.ndim > 1:
                y_proba_positive = y_proba[:, 1]
            else:
                y_proba_positive = y_proba

            metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba_positive))

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm.tolist()

        # Normalized confusion matrix
        cm_normalized = confusion_matrix(y_true, y_pred, normalize="true")
        metrics["confusion_matrix_normalized"] = cm_normalized.tolist()

        # Classification report
        report = classification_report(y_true, y_pred, output_dict=True)
        metrics["classification_report"] = report

        logger.info(f"Evaluation metrics: Accuracy={metrics['accuracy']:.3f}, "
                   f"Precision={metrics['precision']:.3f}, "
                   f"Recall={metrics['recall']:.3f}, "
                   f"F1={metrics['f1_score']:.3f}")

        return metrics

    def compare_models(
        self, models: Dict[str, BaseModel], X: np.ndarray, y_true: np.ndarray
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple models.

        Args:
            models: Dictionary of model name to model instance
            X: Input features
            y_true: True labels

        Returns:
            Dictionary of model names to their metrics
        """
        logger.info(f"Comparing {len(models)} models")

        results = {}

        for model_name, model in models.items():
            logger.info(f"Evaluating {model_name}")
            self.set_model(model)
            metrics = self.evaluate(X, y_true)
            results[model_name] = metrics

        return results

    def get_best_model(
        self,
        models: Dict[str, BaseModel],
        X: np.ndarray,
        y_true: np.ndarray,
        metric: str = "accuracy",
    ) -> tuple:
        """
        Find the best performing model.

        Args:
            models: Dictionary of model name to model instance
            X: Input features
            y_true: True labels
            metric: Metric to use for comparison

        Returns:
            Tuple of (best_model_name, best_model, metrics)
        """
        results = self.compare_models(models, X, y_true)

        # Find best model based on metric
        best_name = max(results, key=lambda name: results[name][metric])
        best_model = models[best_name]
        best_metrics = results[best_name]

        logger.info(f"Best model: {best_name} ({metric}={best_metrics[metric]:.3f})")

        return best_name, best_model, best_metrics
