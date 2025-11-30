"""Script to evaluate models."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipelines.evaluation_pipeline import EvaluationPipeline
from src.utils.logger import setup_logger

logger = setup_logger("evaluate_model")


def main():
    """Main evaluation script."""
    parser = argparse.ArgumentParser(description="Evaluate cancer prediction models")
    parser.add_argument(
        "--model",
        type=str,
        nargs="+",
        default=None,
        help="Model names to evaluate (default: all)",
    )
    parser.add_argument(
        "--test-data",
        type=str,
        default=None,
        help="Path to test data (default: from config)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation_results.json",
        help="Output file for results",
    )

    args = parser.parse_args()

    logger.info("Starting model evaluation")
    logger.info(f"Arguments: {vars(args)}")

    try:
        # Initialize pipeline
        pipeline = EvaluationPipeline()

        # Run evaluation
        results = pipeline.run(
            test_data_path=args.test_data,
            model_names=args.model,
            output_path=args.output,
        )

        # Print summary
        print("\n" + "=" * 80)
        print("EVALUATION COMPLETE")
        print("=" * 80)
        for model_name, metrics in results.items():
            print(f"\n{model_name}:")
            print(f"  Accuracy:  {metrics['accuracy']:.3f}")
            print(f"  Precision: {metrics['precision']:.3f}")
            print(f"  Recall:    {metrics['recall']:.3f}")
            print(f"  F1 Score:  {metrics['f1_score']:.3f}")
            if "roc_auc" in metrics:
                print(f"  ROC AUC:   {metrics['roc_auc']:.3f}")
        print(f"\nResults saved to: {args.output}")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
