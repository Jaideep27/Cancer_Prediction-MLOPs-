"""Script for batch predictions."""

import argparse
import sys
from pathlib import Path

import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipelines.inference_pipeline import InferencePipeline
from src.utils.logger import setup_logger

logger = setup_logger("batch_predict")


def main():
    """Main batch prediction script."""
    parser = argparse.ArgumentParser(description="Batch prediction for cancer diagnosis")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input CSV file with features",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output CSV file for predictions",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="hybrid_ensemble",
        help="Model name to use",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="latest",
        help="Model version to use",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for predictions",
    )

    args = parser.parse_args()

    logger.info("Starting batch prediction")
    logger.info(f"Arguments: {vars(args)}")

    try:
        # Load input data
        logger.info(f"Loading data from {args.input}")
        df = pd.read_csv(args.input)
        logger.info(f"Loaded {len(df)} samples")

        # Initialize pipeline
        pipeline = InferencePipeline(
            model_name=args.model,
            model_version=args.version,
        )

        # Make predictions
        logger.info("Making predictions...")
        result = pipeline.batch_predict(
            df,
            batch_size=args.batch_size,
            return_proba=True,
        )

        # Add predictions to dataframe
        df["prediction"] = result["predictions"]
        df["diagnosis"] = df["prediction"].map({0: "Benign", 1: "Malignant"})
        df["probability_benign"] = result["probabilities"][:, 0]
        df["probability_malignant"] = result["probabilities"][:, 1]

        # Save output
        df.to_csv(args.output, index=False)
        logger.info(f"Predictions saved to {args.output}")

        # Print summary
        print("\n" + "=" * 80)
        print("BATCH PREDICTION COMPLETE")
        print("=" * 80)
        print(f"\nTotal samples: {len(df)}")
        print(f"Predicted Benign: {(df['prediction'] == 0).sum()}")
        print(f"Predicted Malignant: {(df['prediction'] == 1).sum()}")
        print(f"\nOutput saved to: {args.output}")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Batch prediction failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
