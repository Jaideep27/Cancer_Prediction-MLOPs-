"""Feature engineering and selection."""

from typing import List, Optional

import pandas as pd

from ..utils.config import get_config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FeatureBuilder:
    """Feature engineering and selection."""

    def __init__(self, feature_list: Optional[List[str]] = None):
        """
        Initialize feature builder.

        Args:
            feature_list: Optional list of features to use
        """
        if feature_list is None:
            model_config = get_config("model_config")
            self.features = model_config.get("features", [])
        else:
            self.features = feature_list

        self.target = get_config("model_config", "target", default="target")

    def select_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select configured features from dataframe.

        Args:
            df: Input dataframe

        Returns:
            Dataframe with selected features
        """
        # Include target if it exists
        columns_to_select = self.features.copy()
        if self.target in df.columns and self.target not in columns_to_select:
            columns_to_select.append(self.target)

        # Filter to only existing columns
        existing_columns = [col for col in columns_to_select if col in df.columns]
        missing_columns = [col for col in columns_to_select if col not in df.columns]

        if missing_columns:
            logger.warning(f"Missing columns: {missing_columns}")

        logger.info(f"Selected {len(existing_columns)} features")

        return df[existing_columns]

    def get_X_y(self, df: pd.DataFrame) -> tuple:
        """
        Split dataframe into features (X) and target (y).

        Args:
            df: Input dataframe

        Returns:
            Tuple of (X, y)
        """
        if self.target not in df.columns:
            raise ValueError(f"Target column '{self.target}' not found in dataframe")

        X = df[self.features]
        y = df[self.target]

        logger.info(f"Split data into X{X.shape} and y{y.shape}")

        return X, y

    def get_feature_names(self) -> List[str]:
        """
        Get list of feature names.

        Returns:
            List of feature names
        """
        return self.features.copy()
