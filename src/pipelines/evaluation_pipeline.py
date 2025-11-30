"""Model evaluation pipeline."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from ..data.load_data import load_processed_data
from ..features.build_features import FeatureBuilder
from ..models.evaluate import ModelEvaluator
from ..models.registry import ModelRegistry
from ..models.predict import ModelPredictor
from ..utils.helpers import save_json
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EvaluationPipeline:
    """Pipeline for evaluating models on test data."""

    def __init__(self):
        """Initialize evaluation pipeline."""
        self.feature_builder = FeatureBuilder()
        self.evaluator = ModelEvaluator()
        self.registry = ModelRegistry()

        self.results = {}

    def load_test_data(self, filepath: Optional[str] = None) -> None:
        """
        Load test data.

        Args:
            filepath: Optional path to test data file
        """
        logger.info("Loading test data")

        if filepath:
            self.test_data = pd.read_csv(filepath)
        else:
            self.test_data = load_processed_data("test")

        # Prepare features
        self.X_test, self.y_test = self.feature_builder.get_X_y(self.test_data)

        logger.info(f"Loaded {len(self.test_data)} test samples")

    def evaluate_model(
        self, model_name: str, model_version: str = "latest"
    ) -> Dict[str, Any]:
        """
        Evaluate a single model.

        Args:
            model_name: Name of the model
            model_version: Version of the model

        Returns:
            Evaluation metrics
        """
        logger.info(f"Evaluating model: {model_name} v{model_version}")

        # Load model
        model_path = self.registry.get_model_path(model_name, model_version)

        if model_path is None:
            raise FileNotFoundError(
                f"Model not found in registry: {model_name} v{model_version}"
            )

        predictor = ModelPredictor(model_path=str(model_path))

        # Evaluate
        self.evaluator.set_model(predictor.model)
        metrics = self.evaluator.evaluate(self.X_test, self.y_test)

        logger.info(
            f"{model_name} - Accuracy: {metrics['accuracy']:.3f}, "
            f"F1: {metrics['f1_score']:.3f}"
        )

        return metrics

    def evaluate_all_models(
        self, model_names: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate all registered models.

        Args:
            model_names: Optional list of model names to evaluate

        Returns:
            Dictionary of evaluation results
        """
        logger.info("Evaluating all models")

        # Get list of models
        if model_names is None:
            registered_models = self.registry.list_models()
            # Get unique model names
            model_names = list(set([m["model_name"] for m in registered_models]))

        evaluation_results = {}

        for model_name in model_names:
            try:
                metrics = self.evaluate_model(model_name)
                evaluation_results[model_name] = metrics
            except Exception as e:
                logger.error(f"Error evaluating {model_name}: {str(e)}")

        self.results = evaluation_results

        return evaluation_results

    def compare_models(self, model_names: List[str]) -> pd.DataFrame:
        """
        Compare multiple models.

        Args:
            model_names: List of model names to compare

        Returns:
            DataFrame with comparison results
        """
        logger.info(f"Comparing {len(model_names)} models")

        comparison_data = []

        for model_name in model_names:
            metrics = self.evaluate_model(model_name)

            comparison_data.append(
                {
                    "model": model_name,
                    "accuracy": metrics["accuracy"],
                    "precision": metrics["precision"],
                    "recall": metrics["recall"],
                    "f1_score": metrics["f1_score"],
                    "roc_auc": metrics.get("roc_auc", None),
                }
            )

        comparison_df = pd.DataFrame(comparison_data)

        # Sort by accuracy
        comparison_df = comparison_df.sort_values("accuracy", ascending=False)

        logger.info("\nModel Comparison:")
        logger.info("\n" + str(comparison_df))

        return comparison_df

    def save_results(self, output_path: str = "evaluation_results.json") -> None:
        """
        Save evaluation results to file.

        Args:
            output_path: Path to output file
        """
        save_json(self.results, output_path)
        logger.info(f"Evaluation results saved to {output_path}")

    def run(
        self,
        test_data_path: Optional[str] = None,
        model_names: Optional[List[str]] = None,
        save_results: bool = True,
        output_path: str = "evaluation_results.json",
    ) -> Dict[str, Dict[str, Any]]:
        """
        Run complete evaluation pipeline.

        Args:
            test_data_path: Optional path to test data
            model_names: Optional list of models to evaluate
            save_results: Whether to save results
            output_path: Path to save results

        Returns:
            Evaluation results
        """
        logger.info("=" * 80)
        logger.info("Starting Evaluation Pipeline")
        logger.info("=" * 80)

        try:
            # Load test data
            self.load_test_data(test_data_path)

            # Evaluate models
            results = self.evaluate_all_models(model_names)

            # Save results
            if save_results:
                self.save_results(output_path)

            logger.info("=" * 80)
            logger.info("Evaluation Pipeline Complete!")
            logger.info("=" * 80)

            return results

        except Exception as e:
            logger.error(f"Evaluation pipeline failed: {str(e)}")
            raise
