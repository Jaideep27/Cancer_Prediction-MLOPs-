"""Script to train models."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipelines.training_pipeline import TrainingPipeline
from src.utils.helpers import save_json
from src.utils.logger import setup_logger

logger = setup_logger("train_model")


def main():
    """Main training script."""
    parser = argparse.ArgumentParser(description="Train cancer prediction models")
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Path to data file (default: from config)",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="1.0",
        help="Model version (default: 1.0)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save models to registry",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="training_results.json",
        help="Output file for results",
    )

    args = parser.parse_args()

    logger.info("Starting model training")
    logger.info(f"Arguments: {vars(args)}")

    try:
        # Initialize pipeline
        pipeline = TrainingPipeline()

        # Run training
        results = pipeline.run(
            data_filepath=args.data,
            save_models=not args.no_save,
            version=args.version,
        )

        # Save results
        save_json(results, args.output)
        logger.info(f"Results saved to {args.output}")

        # Print summary
        print("\n" + "=" * 80)
        print("TRAINING COMPLETE")
        print("=" * 80)
        print(f"\nBest Model: {results['best_model']['name']}")
        print(f"Accuracy: {results['best_model']['metrics']['accuracy']:.3f}")
        print(f"F1 Score: {results['best_model']['metrics']['f1_score']:.3f}")
        print(f"\nResults saved to: {args.output}")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
