"""Data splitting utilities."""

from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from ..utils.config import get_config
from ..utils.helpers import ensure_dir
from ..utils.logger import get_logger

logger = get_logger(__name__)


def split_data(
    df: pd.DataFrame,
    test_size: float = 0.25,
    validation_size: float = 0.0,
    random_state: int = 0,
    stratify_column: Optional[str] = None,
    save_splits: bool = False,
) -> Tuple[pd.DataFrame, ...]:
    """
    Split data into train, test, and optionally validation sets.

    Args:
        df: Input dataframe
        test_size: Proportion of data for test set
        validation_size: Proportion of remaining data for validation set
        random_state: Random seed for reproducibility
        stratify_column: Column name to stratify split
        save_splits: Whether to save split data to files

    Returns:
        Tuple of (train_df, test_df) or (train_df, val_df, test_df)
    """
    logger.info(f"Splitting data: test_size={test_size}, validation_size={validation_size}")

    # Stratify if column is specified and exists
    stratify = df[stratify_column] if stratify_column and stratify_column in df.columns else None

    # First split: train+val vs test
    train_val, test = train_test_split(
        df, test_size=test_size, random_state=random_state, stratify=stratify
    )

    logger.info(f"Test split: {len(test)} samples ({len(test)/len(df):.2%})")

    # Second split: train vs validation (if validation_size > 0)
    if validation_size > 0:
        # Stratify validation split
        stratify_val = (
            train_val[stratify_column]
            if stratify_column and stratify_column in train_val.columns
            else None
        )

        train, val = train_test_split(
            train_val,
            test_size=validation_size,
            random_state=random_state,
            stratify=stratify_val,
        )

        logger.info(
            f"Train split: {len(train)} samples ({len(train)/len(df):.2%}), "
            f"Validation split: {len(val)} samples ({len(val)/len(df):.2%})"
        )

        if save_splits:
            _save_splits(train, val, test)

        return train, val, test
    else:
        train = train_val
        logger.info(f"Train split: {len(train)} samples ({len(train)/len(df):.2%})")

        if save_splits:
            _save_splits(train, None, test)

        return train, test


def _save_splits(
    train: pd.DataFrame, val: Optional[pd.DataFrame], test: pd.DataFrame
) -> None:
    """
    Save split datasets to files.

    Args:
        train: Training dataframe
        val: Optional validation dataframe
        test: Test dataframe
    """
    data_config = get_config("data_config")
    paths = data_config.get("paths", {})

    # Get output paths
    train_path = Path(paths.get("processed_train", "data/processed/train.csv"))
    test_path = Path(paths.get("processed_test", "data/processed/test.csv"))
    val_path = Path(paths.get("processed_validation", "data/processed/validation.csv"))

    # Ensure directories exist
    ensure_dir(train_path.parent)

    # Save train and test
    logger.info(f"Saving train data to {train_path}")
    train.to_csv(train_path, index=False)

    logger.info(f"Saving test data to {test_path}")
    test.to_csv(test_path, index=False)

    # Save validation if it exists
    if val is not None:
        logger.info(f"Saving validation data to {val_path}")
        val.to_csv(val_path, index=False)

    logger.info("All splits saved successfully")


def load_and_split_data(
    filepath: Optional[str] = None,
    config_name: str = "data_config",
    save_splits: bool = True,
) -> Tuple[pd.DataFrame, ...]:
    """
    Load raw data and split according to configuration.

    Args:
        filepath: Optional path to data file
        config_name: Name of configuration to use
        save_splits: Whether to save split data

    Returns:
        Split dataframes
    """
    from .load_data import load_raw_data
    from .preprocess import DataPreprocessor

    # Load raw data
    df = load_raw_data(filepath)

    # Preprocess
    preprocessor = DataPreprocessor()
    df = preprocessor.preprocess(df)

    # Get split configuration
    split_config = get_config(config_name, "splitting")
    test_size = split_config.get("test_size", 0.25)
    validation_size = split_config.get("validation_size", 0.0)
    random_state = split_config.get("random_state", 0)
    stratify = "target" if split_config.get("stratify", True) else None

    # Split data
    return split_data(
        df,
        test_size=test_size,
        validation_size=validation_size,
        random_state=random_state,
        stratify_column=stratify,
        save_splits=save_splits,
    )
