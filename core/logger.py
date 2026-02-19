import logging
import sys
from logging.handlers import RotatingFileHandler
from core.config import LOG_PATH, LOG_LEVEL

# Ensure log directory exists
LOG_PATH.mkdir(parents=True, exist_ok=True)

_is_configured = False


def configure_logging():
    """
    Configures the root logger with console and file handlers.
    Should be called once at application startup.
    """
    global _is_configured
    if _is_configured:
        return

    # Create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
    )

    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Clear existing handlers to avoid duplication if re-configured
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler
    file_handler = RotatingFileHandler(
        LOG_PATH / "people_scope.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Error Handler
    error_handler = RotatingFileHandler(
        LOG_PATH / "error.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Third-party loggers noise reduction (optional, adjust as needed)
    logging.getLogger("uvicorn.access").handlers = [] # Let root handle it or keep default
    # If we want uvicorn to use our formatting, we can propagate or attach handlers.
    # For now, let's just configure our root.

    _is_configured = True


def get_logger(name: str):
    """
    Returns a logger with the specified name.
    Ensures logging is configured.
    """
    if not _is_configured:
        configure_logging()
    return logging.getLogger(name)
