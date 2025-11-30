"""Data loading utilities."""

from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from ..utils.config import get_config
from ..utils.helpers import get_data_path
from ..utils.logger import get_logger

logger = get_logger(__name__)


def load_raw_data(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Load raw breast cancer dataset.

    Args:
        filepath: Optional custom path to data file

    Returns:
        Raw dataframe
    """
    if filepath is None:
        # Get from config
        data_config = get_config("data_config")
        filepath = data_config.get("paths", {}).get("raw_data", "data/raw/breast-cancer.csv")

    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    logger.info(f"Loading raw data from {filepath}")
    df = pd.read_csv(filepath)

    logger.info(f"Loaded {len(df)} samples with {len(df.columns)} columns")
    return df


def load_processed_data(
    data_type: str = "train", filepath: Optional[str] = None
) -> pd.DataFrame:
    """
    Load processed data.

    Args:
        data_type: Type of data (train, test, validation)
        filepath: Optional custom path to data file

    Returns:
        Processed dataframe
    """
    if filepath is None:
        data_config = get_config("data_config")
        filepath = data_config.get("paths", {}).get(f"processed_{data_type}")

        if filepath is None:
            raise ValueError(f"No config found for processed_{data_type}")

    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Processed data file not found: {filepath}")

    logger.info(f"Loading {data_type} data from {filepath}")
    df = pd.read_csv(filepath)

    logger.info(f"Loaded {len(df)} {data_type} samples")
    return df


def load_train_test_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load both training and testing data.

    Returns:
        Tuple of (train_df, test_df)
    """
    train_df = load_processed_data("train")
    test_df = load_processed_data("test")

    return train_df, test_df
