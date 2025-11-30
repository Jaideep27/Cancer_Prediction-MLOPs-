"""Script for exploratory data analysis."""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.load_data import load_raw_data
from src.utils.helpers import ensure_dir
from src.utils.logger import setup_logger

logger = setup_logger("run_eda")


def plot_distributions(df: pd.DataFrame, output_dir: str) -> None:
    """Plot feature distributions."""
    logger.info("Generating distribution plots")

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    n_cols = len(numeric_cols)

    if n_cols > 30:
        numeric_cols = numeric_cols[:30]  # Limit to first 30

    fig, axes = plt.subplots(5, 6, figsize=(20, 15))
    axes = axes.ravel()

    for idx, col in enumerate(numeric_cols):
        axes[idx].hist(df[col], bins=30, edgecolor="black")
        axes[idx].set_title(col)
        axes[idx].set_ylabel("Frequency")

    plt.tight_layout()
    plt.savefig(Path(output_dir) / "feature_distributions.png", dpi=300)
    plt.close()


def plot_correlation_matrix(df: pd.DataFrame, output_dir: str) -> None:
    """Plot correlation matrix."""
    logger.info("Generating correlation matrix")

    numeric_df = df.select_dtypes(include=["float64", "int64"])

    plt.figure(figsize=(16, 14))
    corr = numeric_df.corr()
    sns.heatmap(corr, cmap="coolwarm", center=0, square=True, linewidths=0.5)
    plt.title("Feature Correlation Matrix")
    plt.tight_layout()
    plt.savefig(Path(output_dir) / "correlation_matrix.png", dpi=300)
    plt.close()


def plot_target_distribution(df: pd.DataFrame, target_col: str, output_dir: str) -> None:
    """Plot target variable distribution."""
    logger.info("Generating target distribution plot")

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    target_counts = df[target_col].value_counts()
    target_counts.plot(kind="bar", ax=ax)
    ax.set_title("Target Variable Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Count")
    ax.set_xticklabels(["Benign", "Malignant"], rotation=0)

    for i, v in enumerate(target_counts):
        ax.text(i, v + 5, str(v), ha="center")

    plt.tight_layout()
    plt.savefig(Path(output_dir) / "target_distribution.png", dpi=300)
    plt.close()


def generate_summary_stats(df: pd.DataFrame, output_dir: str) -> None:
    """Generate and save summary statistics."""
    logger.info("Generating summary statistics")

    summary = df.describe()
    summary.to_csv(Path(output_dir) / "summary_statistics.csv")

    # Missing values
    missing = df.isna().sum()
    missing.to_csv(Path(output_dir) / "missing_values.csv")


def main():
    """Main EDA script."""
    parser = argparse.ArgumentParser(description="Run exploratory data analysis")
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Path to data file (default: from config)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="eda_output",
        help="Output directory for plots and stats",
    )

    args = parser.parse_args()

    logger.info("Starting EDA")
    logger.info(f"Arguments: {vars(args)}")

    try:
        # Create output directory
        ensure_dir(args.output_dir)

        # Load data
        df = load_raw_data(args.data)
        logger.info(f"Loaded {len(df)} samples with {len(df.columns)} columns")

        # Generate visualizations and statistics
        plot_distributions(df, args.output_dir)
        plot_correlation_matrix(df, args.output_dir)

        if "diagnosis" in df.columns:
            plot_target_distribution(df, "diagnosis", args.output_dir)

        generate_summary_stats(df, args.output_dir)

        print("\n" + "=" * 80)
        print("EDA COMPLETE")
        print("=" * 80)
        print(f"\nDataset shape: {df.shape}")
        print(f"Output directory: {args.output_dir}")
        print("\nGenerated files:")
        print("  - feature_distributions.png")
        print("  - correlation_matrix.png")
        print("  - target_distribution.png")
        print("  - summary_statistics.csv")
        print("  - missing_values.csv")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"EDA failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
