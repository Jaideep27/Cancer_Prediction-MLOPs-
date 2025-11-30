"""End-to-end training pipeline."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..data.load_data import load_raw_data
from ..data.preprocess import DataPreprocessor
from ..data.split import split_data
from ..data.validate import DataValidator
from ..features.build_features import FeatureBuilder
from ..models.evaluate import ModelEvaluator
from ..models.registry import ModelRegistry
from ..models.train import ModelTrainer
from ..utils.config import get_config
from ..utils.helpers import save_json
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TrainingPipeline:
    """Complete training pipeline from data loading to model saving."""

    def __init__(self, config_name: str = "training_config"):
        """
        Initialize training pipeline.

        Args:
            config_name: Name of training configuration
        """
        self.config = get_config(config_name)
        self.data_config = get_config("data_config")

        self.preprocessor = DataPreprocessor()
        self.validator = DataValidator()
        self.feature_builder = FeatureBuilder()
        self.trainer = ModelTrainer()
        self.evaluator = ModelEvaluator()
        self.registry = ModelRegistry()

        self.train_data = None
        self.test_data = None
        self.val_data = None

        self.results = {}

    def load_and_validate_data(self, filepath: Optional[str] = None) -> None:
        """
        Load and validate raw data.

        Args:
            filepath: Optional path to data file
        """
        logger.info("Step 1: Loading and validating data")

        # Load raw data
        df = load_raw_data(filepath)

        # Validate raw data
        validation_results = self.validator.validate(df, target_column="diagnosis")

        if not validation_results.get("overall_passed", False):
            logger.warning("Data validation failed, but continuing...")

        self.results["validation"] = validation_results

        # Store raw data
        self.raw_data = df

        logger.info(f"Loaded and validated {len(df)} samples")

    def preprocess_data(self) -> None:
        """Preprocess the data."""
        logger.info("Step 2: Preprocessing data")

        # Preprocess
        self.preprocessed_data = self.preprocessor.preprocess(self.raw_data)

        logger.info(f"Preprocessed data shape: {self.preprocessed_data.shape}")

    def split_dataset(self, save_splits: bool = True) -> None:
        """
        Split data into train/test sets.

        Args:
            save_splits: Whether to save splits to disk
        """
        logger.info("Step 3: Splitting dataset")

        split_config = self.data_config.get("splitting", {})

        result = split_data(
            self.preprocessed_data,
            test_size=split_config.get("test_size", 0.25),
            validation_size=split_config.get("validation_size", 0.0),
            random_state=split_config.get("random_state", 0),
            stratify_column="target" if split_config.get("stratify", True) else None,
            save_splits=save_splits,
        )

        if len(result) == 3:
            self.train_data, self.val_data, self.test_data = result
        else:
            self.train_data, self.test_data = result
            self.val_data = None

        logger.info(
            f"Data split complete: Train={len(self.train_data)}, Test={len(self.test_data)}"
        )

    def prepare_features(self) -> None:
        """Prepare features for training."""
        logger.info("Step 4: Preparing features")

        # Extract X and y
        self.X_train, self.y_train = self.feature_builder.get_X_y(self.train_data)
        self.X_test, self.y_test = self.feature_builder.get_X_y(self.test_data)

        if self.val_data is not None:
            self.X_val, self.y_val = self.feature_builder.get_X_y(self.val_data)

        logger.info(f"Features prepared: {len(self.feature_builder.get_feature_names())} features")

    def train_models(self, models_to_train: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Train models.

        Args:
            models_to_train: Optional list of model names to train

        Returns:
            Dictionary of trained models
        """
        logger.info("Step 5: Training models")

        if models_to_train is None:
            models_to_train = self.config.get("models_to_train")

        # Train all models
        trained_models = self.trainer.train_all_models(
            self.X_train, self.y_train, models_to_train=models_to_train
        )

        self.trained_models = trained_models

        logger.info(f"Trained {len(trained_models)} models")

        return trained_models

    def evaluate_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate all trained models.

        Returns:
            Dictionary of model evaluations
        """
        logger.info("Step 6: Evaluating models")

        evaluation_results = {}

        for model_name, model in self.trained_models.items():
            logger.info(f"Evaluating {model_name}")

            self.evaluator.set_model(model)
            metrics = self.evaluator.evaluate(self.X_test, self.y_test)

            evaluation_results[model_name] = metrics

            logger.info(
                f"{model_name} - Accuracy: {metrics['accuracy']:.3f}, "
                f"F1: {metrics['f1_score']:.3f}, "
                f"ROC-AUC: {metrics.get('roc_auc', 'N/A')}"
            )

        self.results["evaluation"] = evaluation_results

        return evaluation_results

    def save_models(self, version: str = "1.0") -> None:
        """
        Save all trained models to registry.

        Args:
            version: Version identifier
        """
        logger.info("Step 7: Saving models to registry")

        for model_name, model in self.trained_models.items():
            # Get evaluation metrics
            metrics = self.results["evaluation"].get(model_name, {})

            # Register model
            model_id = self.registry.register_model(
                model=model,
                model_name=model_name,
                version=version,
                metrics=metrics,
                metadata={
                    "training_config": self.config,
                    "feature_count": len(self.feature_builder.get_feature_names()),
                    "training_samples": len(self.X_train),
                    "test_samples": len(self.X_test),
                },
            )

            logger.info(f"Registered model: {model_id}")

        logger.info("All models saved to registry")

    def run(
        self,
        data_filepath: Optional[str] = None,
        save_splits: bool = True,
        save_models: bool = True,
        version: str = "1.0",
    ) -> Dict[str, Any]:
        """
        Run complete training pipeline.

        Args:
            data_filepath: Optional path to data file
            save_splits: Whether to save data splits
            save_models: Whether to save trained models
            version: Model version

        Returns:
            Dictionary with pipeline results
        """
        logger.info("=" * 80)
        logger.info("Starting Training Pipeline")
        logger.info("=" * 80)

        try:
            # Run pipeline steps
            self.load_and_validate_data(data_filepath)
            self.preprocess_data()
            self.split_dataset(save_splits=save_splits)
            self.prepare_features()
            self.train_models()
            self.evaluate_models()

            if save_models:
                self.save_models(version=version)

            # Find best model
            best_model_name, best_model, best_metrics = self.evaluator.get_best_model(
                self.trained_models, self.X_test, self.y_test
            )

            self.results["best_model"] = {
                "name": best_model_name,
                "metrics": best_metrics,
            }

            logger.info("=" * 80)
            logger.info("Training Pipeline Complete!")
            logger.info(f"Best Model: {best_model_name}")
            logger.info(f"Best Accuracy: {best_metrics['accuracy']:.3f}")
            logger.info("=" * 80)

            return self.results

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise
