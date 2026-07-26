"""Logging configuration for Despatch."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setupLogging(level: str = "ERROR", log_directory: str | None = None) -> logging.Logger:
    """Configure the Despatch logger once.

    Args:
        level: DEBUG, INFO, WARNING, or ERROR.
        log_directory: Optional directory for a rotating log file.

    Returns:
        Configured Despatch root logger.

    """
    logger = logging.getLogger("despatch")
    logger.setLevel(getattr(logging, level.upper(), logging.ERROR))
    logger.propagate = False
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_directory:
        directory = Path(log_directory)
        directory.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            directory / "despatch.log",
            maxBytes=2 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def getLogger(module_name: str) -> logging.Logger:
    """Return a child logger.

    Args:
        module_name: Usually the caller's ``__name__``.

    Returns:
        Namespaced logger.

    """
    normalized_name = module_name.removeprefix("despatch.")
    return logging.getLogger(f"despatch.{normalized_name}")
