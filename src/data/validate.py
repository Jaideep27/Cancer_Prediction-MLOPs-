"""Data validation utilities."""

from typing import Dict, List, Optional

import pandas as pd

from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataValidator:
    """Data validation and quality checks."""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize validator.

        Args:
            config: Optional validation configuration
        """
        if config is None:
            self.config = get_config("data_config", "validation")
        else:
            self.config = config

    def check_missing_values(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Check for missing values.

        Args:
            df: Input dataframe

        Returns:
            Dictionary with validation results
        """
        missing_counts = df.isna().sum()
        total_missing = missing_counts.sum()
        missing_ratio = total_missing / (len(df) * len(df.columns))

        max_ratio = self.config.get("max_missing_ratio", 0.05)

        result = {
            "passed": missing_ratio <= max_ratio,
            "total_missing": int(total_missing),
            "missing_ratio": float(missing_ratio),
            "max_allowed_ratio": max_ratio,
            "columns_with_missing": missing_counts[missing_counts > 0].to_dict(),
        }

        if result["passed"]:
            logger.info(f"Missing values check PASSED ({missing_ratio:.2%} missing)")
        else:
            logger.warning(
                f"Missing values check FAILED ({missing_ratio:.2%} > {max_ratio:.2%})"
            )

        return result

    def check_duplicates(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Check for duplicate rows.

        Args:
            df: Input dataframe

        Returns:
            Dictionary with validation results
        """
        duplicate_count = df.duplicated().sum()
        duplicate_ratio = duplicate_count / len(df)

        result = {
            "passed": duplicate_count == 0,
            "duplicate_count": int(duplicate_count),
            "duplicate_ratio": float(duplicate_ratio),
        }

        if result["passed"]:
            logger.info("Duplicate check PASSED (no duplicates found)")
        else:
            logger.warning(f"Duplicate check FAILED ({duplicate_count} duplicates found)")

        return result

    def check_target_balance(self, df: pd.DataFrame, target_column: str = "target") -> Dict[str, any]:
        """
        Check target variable balance.

        Args:
            df: Input dataframe
            target_column: Name of target column

        Returns:
            Dictionary with validation results
        """
        if target_column not in df.columns:
            return {
                "passed": False,
                "error": f"Target column '{target_column}' not found",
            }

        value_counts = df[target_column].value_counts()
        class_ratios = (value_counts / len(df)).to_dict()

        # Check if minority class is at least 10% of data
        min_ratio = min(class_ratios.values())
        passed = min_ratio >= 0.1

        result = {
            "passed": passed,
            "class_counts": value_counts.to_dict(),
            "class_ratios": class_ratios,
            "min_class_ratio": float(min_ratio),
        }

        if result["passed"]:
            logger.info(f"Target balance check PASSED (min ratio: {min_ratio:.2%})")
        else:
            logger.warning(f"Target balance check FAILED (min ratio: {min_ratio:.2%} < 10%)")

        return result

    def check_min_samples(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Check if dataset has minimum required samples.

        Args:
            df: Input dataframe

        Returns:
            Dictionary with validation results
        """
        min_samples = self.config.get("min_samples", 100)
        sample_count = len(df)

        result = {
            "passed": sample_count >= min_samples,
            "sample_count": sample_count,
            "min_required": min_samples,
        }

        if result["passed"]:
            logger.info(f"Sample count check PASSED ({sample_count} >= {min_samples})")
        else:
            logger.warning(f"Sample count check FAILED ({sample_count} < {min_samples})")

        return result

    def check_feature_types(self, df: pd.DataFrame, expected_features: Optional[List[str]] = None) -> Dict[str, any]:
        """
        Check if expected features exist and have correct types.

        Args:
            df: Input dataframe
            expected_features: List of expected feature names

        Returns:
            Dictionary with validation results
        """
        if expected_features is None:
            data_config = get_config("data_config")
            expected_features = data_config.get("features", {}).get("numeric_features", [])

        missing_features = [f for f in expected_features if f not in df.columns]
        present_features = [f for f in expected_features if f in df.columns]

        # Check data types of present features
        non_numeric = []
        for feature in present_features:
            if df[feature].dtype not in ["int64", "float64", "int32", "float32"]:
                non_numeric.append(feature)

        result = {
            "passed": len(missing_features) == 0 and len(non_numeric) == 0,
            "missing_features": missing_features,
            "non_numeric_features": non_numeric,
            "total_features": len(expected_features),
            "present_features": len(present_features),
        }

        if result["passed"]:
            logger.info(f"Feature type check PASSED ({len(present_features)} features validated)")
        else:
            logger.warning(
                f"Feature type check FAILED (missing: {len(missing_features)}, non-numeric: {len(non_numeric)})"
            )

        return result

    def validate(self, df: pd.DataFrame, target_column: str = "target") -> Dict[str, any]:
        """
        Run all validation checks.

        Args:
            df: Input dataframe
            target_column: Name of target column

        Returns:
            Dictionary with all validation results
        """
        logger.info(f"Running validation checks on dataset with shape {df.shape}")

        results = {
            "sample_count": self.check_min_samples(df) if self.config.get("check_min_samples", True) else None,
            "missing_values": self.check_missing_values(df) if self.config.get("check_missing_values", True) else None,
            "duplicates": self.check_duplicates(df) if self.config.get("check_duplicates", True) else None,
            "target_balance": self.check_target_balance(df, target_column) if self.config.get("check_target_balance", True) else None,
        }

        # Remove None results
        results = {k: v for k, v in results.items() if v is not None}

        # Overall pass/fail
        all_passed = all(result.get("passed", False) for result in results.values())
        results["overall_passed"] = all_passed

        if all_passed:
            logger.info("All validation checks PASSED")
        else:
            failed_checks = [k for k, v in results.items() if not v.get("passed", False)]
            logger.warning(f"Validation FAILED. Failed checks: {failed_checks}")

        return results
