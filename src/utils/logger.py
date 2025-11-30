"""Logging utilities for the application."""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional

import yaml


def setup_logger(
    name: str = "cancer_mlops",
    config_path: Optional[str] = None,
    log_level: str = "INFO",
) -> logging.Logger:
    """
    Setup logger with configuration.

    Args:
        name: Logger name
        config_path: Path to logging config file
        log_level: Logging level

    Returns:
        Configured logger
    """
    if config_path and Path(config_path).exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
        logger = logging.getLogger(name)
    else:
        # Fallback to basic configuration
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper()))

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        # Add handler
        if not logger.handlers:
            logger.addHandler(console_handler)

    return logger


def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get or create a logger.

    Args:
        name: Logger name
        log_level: Logging level

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level.upper()))

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger
