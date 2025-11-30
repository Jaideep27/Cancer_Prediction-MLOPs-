"""Unit tests for data preprocessing."""

import pandas as pd
import pytest

from src.data.preprocess import DataPreprocessor
from src.data.validate import DataValidator


class TestDataPreprocessor:
    """Tests for DataPreprocessor class."""

    def test_drop_columns(self, sample_data):
        """Test dropping columns."""
        config = {"drop_columns": ["radius_mean"]}
        preprocessor = DataPreprocessor(config=config)

        result = preprocessor.drop_columns(sample_data)

        assert "radius_mean" not in result.columns
        assert len(result.columns) == len(sample_data.columns) - 1

    def test_encode_labels(self, sample_data):
        """Test label encoding."""
        # Add categorical diagnosis column
        sample_data["diagnosis"] = sample_data["target"].map({0: "B", 1: "M"})

        config = {
            "label_encoding": {
                "column": "diagnosis",
                "mapping": {"M": 1, "B": 0}
            }
        }
        preprocessor = DataPreprocessor(config=config)

        result = preprocessor.encode_labels(sample_data)

        assert all(result["diagnosis"].isin([0, 1]))

    def test_rename_columns(self, sample_data):
        """Test column renaming."""
        config = {"rename_columns": {"target": "label"}}
        preprocessor = DataPreprocessor(config=config)

        result = preprocessor.rename_columns(sample_data)

        assert "label" in result.columns
        assert "target" not in result.columns

    def test_handle_missing_values_drop(self, sample_data):
        """Test missing value handling with drop strategy."""
        # Add missing values
        sample_data.iloc[0, 0] = None

        config = {"handle_missing_values": "drop"}
        preprocessor = DataPreprocessor(config=config)

        result = preprocessor.handle_missing_values(sample_data)

        assert len(result) == len(sample_data) - 1
        assert result.isna().sum().sum() == 0


class TestDataValidator:
    """Tests for DataValidator class."""

    def test_check_missing_values(self, sample_data):
        """Test missing value check."""
        validator = DataValidator()

        result = validator.check_missing_values(sample_data)

        assert result["passed"] is True
        assert result["total_missing"] == 0

    def test_check_duplicates(self, sample_data):
        """Test duplicate check."""
        validator = DataValidator()

        result = validator.check_duplicates(sample_data)

        assert result["passed"] is True
        assert result["duplicate_count"] == 0

    def test_check_target_balance(self, sample_data):
        """Test target balance check."""
        validator = DataValidator()

        result = validator.check_target_balance(sample_data, "target")

        assert "class_counts" in result
        assert "class_ratios" in result

    def test_check_min_samples(self, sample_data):
        """Test minimum samples check."""
        config = {"min_samples": 50}
        validator = DataValidator(config=config)

        result = validator.check_min_samples(sample_data)

        assert result["passed"] is True
        assert result["sample_count"] == len(sample_data)

    def test_validate_all(self, sample_data):
        """Test full validation."""
        validator = DataValidator()

        result = validator.validate(sample_data, "target")

        assert "overall_passed" in result
        assert "missing_values" in result
        assert "duplicates" in result
