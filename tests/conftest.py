"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_data():
    """Create sample cancer data for testing."""
    np.random.seed(42)

    n_samples = 100
    n_features = 30

    # Generate random features
    data = np.random.randn(n_samples, n_features)

    # Create feature names
    feature_prefixes = ["radius", "texture", "perimeter", "area", "smoothness",
                       "compactness", "concavity", "concave points", "symmetry",
                       "fractal_dimension"]
    feature_suffixes = ["_mean", "_se", "_worst"]

    features = [f"{prefix}{suffix}" for prefix in feature_prefixes for suffix in feature_suffixes]

    # Create DataFrame
    df = pd.DataFrame(data, columns=features)

    # Add target
    df["target"] = np.random.randint(0, 2, n_samples)

    return df


@pytest.fixture
def sample_features():
    """Create sample feature dictionary."""
    return {
        "radius_mean": 17.99,
        "texture_mean": 10.38,
        "perimeter_mean": 122.8,
        "area_mean": 1001.0,
        "smoothness_mean": 0.1184,
        "compactness_mean": 0.2776,
        "concavity_mean": 0.3001,
        "concave points_mean": 0.1471,
        "symmetry_mean": 0.2419,
        "fractal_dimension_mean": 0.07871,
        "radius_se": 1.095,
        "texture_se": 0.9053,
        "perimeter_se": 8.589,
        "area_se": 153.4,
        "smoothness_se": 0.006399,
        "compactness_se": 0.04904,
        "concavity_se": 0.05373,
        "concave points_se": 0.01587,
        "symmetry_se": 0.03003,
        "fractal_dimension_se": 0.006193,
        "radius_worst": 25.38,
        "texture_worst": 17.33,
        "perimeter_worst": 184.6,
        "area_worst": 2019.0,
        "smoothness_worst": 0.1622,
        "compactness_worst": 0.6656,
        "concavity_worst": 0.7119,
        "concave points_worst": 0.2654,
        "symmetry_worst": 0.4601,
        "fractal_dimension_worst": 0.1189,
    }


@pytest.fixture
def sample_X_y(sample_data):
    """Create sample X and y arrays."""
    feature_cols = [col for col in sample_data.columns if col != "target"]
    X = sample_data[feature_cols].values
    y = sample_data["target"].values
    return X, y


@pytest.fixture
def tmp_model_dir(tmp_path):
    """Create temporary model directory."""
    model_dir = tmp_path / "models" / "test_model"
    model_dir.mkdir(parents=True)
    return model_dir
