"""Logging configuration for envoy_despatch."""

import logging
import os
import sys


def setupLogging(level: str = "ERROR", log_directory: str | None = None) -> logging.Logger:
    """Configure the application logger.

    Args:
        level: Logging level string (DEBUG, INFO, WARN, ERROR). Defaults to ERROR.
        log_directory: Optional directory path to write log files to.

    Returns:
        Configured root logger instance.

    """
    logger = logging.getLogger("despatch")
    logger.setLevel(getattr(logging, level.upper(), logging.ERROR))

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_directory:
        os.makedirs(log_directory, exist_ok=True)
        log_file = os.path.join(log_directory, "despatch.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger with the given name.

    Args:
        name: Logger name (typically ``__name__``).

    Returns:
        Logger instance.

    """
    return logging.getLogger(f"despatch.{name}")
