"""Data drift detection utilities."""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataDriftDetector:
    """Detect data drift in features."""

    def __init__(self, reference_data: Optional[pd.DataFrame] = None):
        """
        Initialize drift detector.

        Args:
            reference_data: Reference dataset for comparison
        """
        self.reference_data = reference_data
        self.reference_stats = None

        if reference_data is not None:
            self._calculate_reference_stats()

    def set_reference_data(self, reference_data: pd.DataFrame) -> None:
        """
        Set reference dataset.

        Args:
            reference_data: Reference dataset
        """
        self.reference_data = reference_data
        self._calculate_reference_stats()

    def _calculate_reference_stats(self) -> None:
        """Calculate statistics for reference data."""
        self.reference_stats = {
            "mean": self.reference_data.mean().to_dict(),
            "std": self.reference_data.std().to_dict(),
            "min": self.reference_data.min().to_dict(),
            "max": self.reference_data.max().to_dict(),
            "median": self.reference_data.median().to_dict(),
        }

        logger.info("Reference statistics calculated")

    def detect_drift_ks_test(
        self, current_data: pd.DataFrame, threshold: float = 0.05
    ) -> Dict[str, any]:
        """
        Detect drift using Kolmogorov-Smirnov test.

        Args:
            current_data: Current dataset to compare
            threshold: P-value threshold for drift detection

        Returns:
            Dictionary with drift detection results
        """
        if self.reference_data is None:
            raise ValueError("Reference data not set")

        drift_results = {}
        drifted_features = []

        for column in self.reference_data.columns:
            if column not in current_data.columns:
                continue

            # KS test
            statistic, p_value = stats.ks_2samp(
                self.reference_data[column], current_data[column]
            )

            is_drifted = p_value < threshold

            drift_results[column] = {
                "ks_statistic": float(statistic),
                "p_value": float(p_value),
                "drifted": is_drifted,
            }

            if is_drifted:
                drifted_features.append(column)

        summary = {
            "total_features": len(drift_results),
            "drifted_features": drifted_features,
            "drift_count": len(drifted_features),
            "drift_percentage": len(drifted_features) / len(drift_results) * 100,
            "threshold": threshold,
            "details": drift_results,
        }

        if drifted_features:
            logger.warning(
                f"Data drift detected in {len(drifted_features)} features: {drifted_features}"
            )
        else:
            logger.info("No data drift detected")

        return summary

    def detect_drift_statistics(
        self, current_data: pd.DataFrame, threshold: float = 0.2
    ) -> Dict[str, any]:
        """
        Detect drift by comparing statistical properties.

        Args:
            current_data: Current dataset
            threshold: Threshold for relative change

        Returns:
            Dictionary with drift detection results
        """
        if self.reference_stats is None:
            raise ValueError("Reference statistics not calculated")

        current_stats = {
            "mean": current_data.mean().to_dict(),
            "std": current_data.std().to_dict(),
        }

        drift_results = {}
        drifted_features = []

        for column in self.reference_stats["mean"].keys():
            if column not in current_data.columns:
                continue

            ref_mean = self.reference_stats["mean"][column]
            cur_mean = current_stats["mean"][column]

            ref_std = self.reference_stats["std"][column]
            cur_std = current_stats["std"][column]

            # Calculate relative changes
            mean_change = abs((cur_mean - ref_mean) / ref_mean) if ref_mean != 0 else 0
            std_change = abs((cur_std - ref_std) / ref_std) if ref_std != 0 else 0

            is_drifted = (mean_change > threshold) or (std_change > threshold)

            drift_results[column] = {
                "mean_change": float(mean_change),
                "std_change": float(std_change),
                "reference_mean": float(ref_mean),
                "current_mean": float(cur_mean),
                "reference_std": float(ref_std),
                "current_std": float(cur_std),
                "drifted": is_drifted,
            }

            if is_drifted:
                drifted_features.append(column)

        summary = {
            "total_features": len(drift_results),
            "drifted_features": drifted_features,
            "drift_count": len(drifted_features),
            "threshold": threshold,
            "details": drift_results,
        }

        return summary

    def get_feature_distribution_summary(
        self, data: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """
        Get distribution summary for features.

        Args:
            data: Dataset to summarize

        Returns:
            Dictionary with feature distributions
        """
        summary = {}

        for column in data.columns:
            summary[column] = {
                "mean": float(data[column].mean()),
                "std": float(data[column].std()),
                "min": float(data[column].min()),
                "max": float(data[column].max()),
                "median": float(data[column].median()),
                "q25": float(data[column].quantile(0.25)),
                "q75": float(data[column].quantile(0.75)),
            }

        return summary
