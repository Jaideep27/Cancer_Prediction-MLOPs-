"""Data preprocessing utilities."""

from typing import Dict, List, Optional

import pandas as pd
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataPreprocessor:
    """Data preprocessing pipeline."""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize preprocessor.

        Args:
            config: Optional preprocessing configuration
        """
        if config is None:
            self.config = get_config("data_config", "preprocessing")
        else:
            self.config = config

        self.scaler = None
        self._initialize_scaler()

    def _initialize_scaler(self) -> None:
        """Initialize scaler based on configuration."""
        scaling_config = self.config.get("scaling", {})
        method = scaling_config.get("method", "none")

        if method == "standard":
            self.scaler = StandardScaler()
        elif method == "minmax":
            self.scaler = MinMaxScaler()
        elif method == "robust":
            self.scaler = RobustScaler()
        else:
            self.scaler = None

    def drop_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop specified columns.

        Args:
            df: Input dataframe

        Returns:
            Dataframe with columns dropped
        """
        drop_cols = self.config.get("drop_columns", [])

        if not drop_cols:
            return df

        existing_cols = [col for col in drop_cols if col in df.columns]

        if existing_cols:
            logger.info(f"Dropping columns: {existing_cols}")
            df = df.drop(columns=existing_cols)

        return df

    def encode_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Encode categorical labels to numeric.

        Args:
            df: Input dataframe

        Returns:
            Dataframe with encoded labels
        """
        label_config = self.config.get("label_encoding", {})

        if not label_config:
            return df

        column = label_config.get("column")
        mapping = label_config.get("mapping", {})

        if column and column in df.columns and mapping:
            logger.info(f"Encoding column '{column}' with mapping: {mapping}")
            for key, value in mapping.items():
                df.loc[df[column] == key, column] = value

            # Ensure encoded column is integer type
            df[column] = df[column].astype(int)

        return df

    def rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns.

        Args:
            df: Input dataframe

        Returns:
            Dataframe with renamed columns
        """
        rename_map = self.config.get("rename_columns", {})

        if rename_map:
            logger.info(f"Renaming columns: {rename_map}")
            df = df.rename(columns=rename_map)

        return df

    def convert_to_int(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert numeric columns to int where appropriate.

        Args:
            df: Input dataframe

        Returns:
            Dataframe with converted types
        """
        if not self.config.get("convert_to_int", False):
            return df

        logger.info("Converting appropriate columns to int type")

        # Don't convert the target column if it exists
        target_col = self.config.get("rename_columns", {}).get("diagnosis", "target")

        for col in df.columns:
            # Skip target column - it should already be int from encoding
            if col == target_col:
                continue

            if df[col].dtype in ["float64", "float32"]:
                # Check if all non-null values are integers
                if df[col].notna().all() and (df[col] == df[col].astype(int)).all():
                    df[col] = df[col].astype(int)

        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values.

        Args:
            df: Input dataframe

        Returns:
            Dataframe with missing values handled
        """
        strategy = self.config.get("handle_missing_values", "drop")

        missing_count = df.isna().sum().sum()
        if missing_count == 0:
            logger.info("No missing values found")
            return df

        logger.info(f"Handling {missing_count} missing values using strategy: {strategy}")

        if strategy == "drop":
            df = df.dropna()
        elif strategy == "impute":
            # Simple mean imputation for numeric columns
            numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        # else: do nothing

        return df

    def scale_features(
        self, df: pd.DataFrame, fit: bool = True, exclude_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Scale numeric features.

        Args:
            df: Input dataframe
            fit: Whether to fit the scaler
            exclude_columns: Columns to exclude from scaling

        Returns:
            Dataframe with scaled features
        """
        if self.scaler is None:
            return df

        if exclude_columns is None:
            scaling_config = self.config.get("scaling", {})
            exclude_columns = scaling_config.get("exclude_columns", [])

        # Get numeric columns to scale
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        cols_to_scale = [col for col in numeric_cols if col not in exclude_columns]

        if not cols_to_scale:
            return df

        logger.info(f"Scaling {len(cols_to_scale)} features")

        if fit:
            df[cols_to_scale] = self.scaler.fit_transform(df[cols_to_scale])
        else:
            df[cols_to_scale] = self.scaler.transform(df[cols_to_scale])

        return df

    def preprocess(self, df: pd.DataFrame, fit_scaler: bool = True) -> pd.DataFrame:
        """
        Run full preprocessing pipeline.

        Args:
            df: Input dataframe
            fit_scaler: Whether to fit the scaler

        Returns:
            Preprocessed dataframe
        """
        logger.info(f"Starting preprocessing pipeline on {len(df)} samples")

        # Make a copy to avoid modifying original
        df = df.copy()

        # Apply preprocessing steps in order
        df = self.drop_columns(df)
        df = self.encode_labels(df)
        df = self.rename_columns(df)
        df = self.handle_missing_values(df)
        df = self.convert_to_int(df)
        df = self.scale_features(df, fit=fit_scaler)

        logger.info(f"Preprocessing complete. Output shape: {df.shape}")

        return df
