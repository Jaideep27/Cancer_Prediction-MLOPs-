"""Helper utility functions."""

import json
import pickle
from pathlib import Path
from typing import Any, Dict, Optional

import joblib


def ensure_dir(path: str) -> Path:
    """
    Ensure directory exists, create if it doesn't.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save data to JSON file.

    Args:
        data: Data to save
        filepath: Output file path
    """
    ensure_dir(Path(filepath).parent)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load data from JSON file.

    Args:
        filepath: Input file path

    Returns:
        Loaded data
    """
    with open(filepath, "r") as f:
        return json.load(f)


def save_pickle(obj: Any, filepath: str, compress: bool = False) -> None:
    """
    Save object using pickle.

    Args:
        obj: Object to save
        filepath: Output file path
        compress: Whether to use compression (joblib)
    """
    ensure_dir(Path(filepath).parent)

    if compress:
        joblib.dump(obj, filepath, compress=3)
    else:
        with open(filepath, "wb") as f:
            pickle.dump(obj, f)


def load_pickle(filepath: str) -> Any:
    """
    Load object from pickle file.

    Args:
        filepath: Input file path

    Returns:
        Loaded object
    """
    try:
        # Try joblib first (handles compression)
        return joblib.load(filepath)
    except Exception:
        # Fallback to standard pickle
        with open(filepath, "rb") as f:
            return pickle.load(f)


def get_project_root() -> Path:
    """
    Get project root directory.

    Returns:
        Project root path
    """
    return Path(__file__).parent.parent.parent


def get_model_path(model_name: str, version: str = "latest") -> Path:
    """
    Get model directory path.

    Args:
        model_name: Name of the model
        version: Model version

    Returns:
        Model directory path
    """
    root = get_project_root()
    return root / "models" / model_name


def get_data_path(data_type: str = "raw") -> Path:
    """
    Get data directory path.

    Args:
        data_type: Type of data (raw, processed, external)

    Returns:
        Data directory path
    """
    root = get_project_root()
    return root / "data" / data_type
