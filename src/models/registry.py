"""Model registry for managing model versions and metadata."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_model import BaseModel
from ..utils.helpers import ensure_dir, save_json, load_json
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelRegistry:
    """Manages model versions and metadata."""

    def __init__(self, registry_path: str = "models"):
        """
        Initialize model registry.

        Args:
            registry_path: Base path for model registry
        """
        self.registry_path = Path(registry_path)
        ensure_dir(self.registry_path)

        self.registry_file = self.registry_path / "registry.json"
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """
        Load registry from disk.

        Returns:
            Registry dictionary
        """
        if self.registry_file.exists():
            return load_json(str(self.registry_file))
        else:
            return {"models": {}}

    def _save_registry(self) -> None:
        """Save registry to disk."""
        save_json(self.registry, str(self.registry_file))

    def register_model(
        self,
        model: BaseModel,
        model_name: str,
        version: str,
        metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Register a model in the registry.

        Args:
            model: Model instance to register
            model_name: Name of the model
            version: Version identifier
            metrics: Model performance metrics
            metadata: Additional metadata

        Returns:
            Model ID
        """
        model_id = f"{model_name}_v{version}"

        # Create model directory
        model_dir = self.registry_path / model_name / version
        ensure_dir(model_dir)

        # Save model
        model.save(str(model_dir), metadata=metadata)

        # Create registry entry
        entry = {
            "model_id": model_id,
            "model_name": model_name,
            "version": version,
            "path": str(model_dir),
            "registered_at": datetime.now().isoformat(),
            "metrics": metrics or {},
            "metadata": metadata or {},
            "status": "active",
        }

        # Add to registry
        if model_name not in self.registry["models"]:
            self.registry["models"][model_name] = {}

        self.registry["models"][model_name][version] = entry

        # Save metrics
        if metrics:
            metrics_file = model_dir / "metrics.json"
            save_json(metrics, str(metrics_file))

        self._save_registry()

        logger.info(f"Registered model: {model_id} at {model_dir}")

        return model_id

    def get_model_path(self, model_name: str, version: str = "latest") -> Optional[Path]:
        """
        Get path to a registered model.

        Args:
            model_name: Name of the model
            version: Version identifier (default: latest)

        Returns:
            Path to model or None if not found
        """
        if model_name not in self.registry["models"]:
            logger.warning(f"Model not found in registry: {model_name}")
            return None

        versions = self.registry["models"][model_name]

        if not versions:
            logger.warning(f"No versions found for model: {model_name}")
            return None

        if version == "latest":
            # Get the most recent version
            latest_version = max(
                versions.items(), key=lambda x: x[1].get("registered_at", "")
            )[0]
            version = latest_version

        if version not in versions:
            logger.warning(f"Version {version} not found for model: {model_name}")
            return None

        model_path = Path(versions[version]["path"])

        if not model_path.exists():
            logger.warning(f"Model path does not exist: {model_path}")
            return None

        return model_path

    def get_model_info(self, model_name: str, version: str = "latest") -> Optional[Dict[str, Any]]:
        """
        Get information about a registered model.

        Args:
            model_name: Name of the model
            version: Version identifier

        Returns:
            Model information dictionary
        """
        if model_name not in self.registry["models"]:
            return None

        versions = self.registry["models"][model_name]

        if version == "latest":
            latest_version = max(
                versions.items(), key=lambda x: x[1].get("registered_at", "")
            )[0]
            version = latest_version

        return versions.get(version)

    def list_models(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List registered models.

        Args:
            model_name: Optional filter by model name

        Returns:
            List of model information dictionaries
        """
        models = []

        if model_name:
            if model_name in self.registry["models"]:
                for version_info in self.registry["models"][model_name].values():
                    models.append(version_info)
        else:
            for model_versions in self.registry["models"].values():
                for version_info in model_versions.values():
                    models.append(version_info)

        return models

    def delete_model(self, model_name: str, version: str) -> bool:
        """
        Delete a model from registry.

        Args:
            model_name: Name of the model
            version: Version identifier

        Returns:
            True if deleted, False otherwise
        """
        if model_name not in self.registry["models"]:
            return False

        if version not in self.registry["models"][model_name]:
            return False

        # Mark as deleted (don't actually remove from disk for safety)
        self.registry["models"][model_name][version]["status"] = "deleted"
        self._save_registry()

        logger.info(f"Marked model as deleted: {model_name} v{version}")

        return True

    def promote_model(self, model_name: str, version: str, stage: str = "production") -> bool:
        """
        Promote a model to a specific stage.

        Args:
            model_name: Name of the model
            version: Version identifier
            stage: Stage to promote to (e.g., 'production', 'staging')

        Returns:
            True if promoted, False otherwise
        """
        if model_name not in self.registry["models"]:
            return False

        if version not in self.registry["models"][model_name]:
            return False

        # Update stage
        self.registry["models"][model_name][version]["stage"] = stage
        self._save_registry()

        logger.info(f"Promoted model to {stage}: {model_name} v{version}")

        return True
