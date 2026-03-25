import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


# Lazy config getter to avoid circular import
def _get_log_level():
    try:
        from soul.core.config import config

        return getattr(logging, config.log_level.upper(), logging.INFO)
    except (ImportError, AttributeError):
        return logging.INFO


def setup_logger(name: str) -> logging.Logger:
    """Configures and returns a centralized logger."""
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Get log level (lazy import to avoid circular dependency)
    level = _get_log_level()
    logger.setLevel(level)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Directory for logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "soul_system.log"

    # Rotating File Handler (10MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)

    # Standardized Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Prevent propagation to the root logger to avoid double logging
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Alias for setup_logger for consistency."""
    return setup_logger(name)
