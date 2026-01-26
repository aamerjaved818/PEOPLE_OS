import logging
import os
import sys

# Ensure we can find the config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.config import settings
except ImportError:
    # Fallback if running from root
    from config import settings


def configure_logging():
    """
    Configure structured logging for the application.
    Uses generic logging for now, upgradeable to JSON later.
    """
    log_level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO

    # Create Logger
    logger = logging.getLogger("peopleOS eBusiness")
    logger.setLevel(log_level)

    # Ensure logs directory exists (project-level `logs/`)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # File handler (rotating)
    log_file = os.path.join(logs_dir, "people_os.log")
    try:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=7, encoding="utf-8")
        file_handler.setLevel(log_level)
    except Exception:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Formatter
    if settings.ENVIRONMENT == "production":
        try:
            from pythonjsonlogger import jsonlogger

            formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s %(filename)s %(lineno)d"
            )
        except ImportError:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Attach handlers (avoid duplicate handlers)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(console_handler)
    if not any(getattr(h, "baseFilename", None) == os.path.abspath(log_file) for h in logger.handlers if hasattr(h, "baseFilename")):
        logger.addHandler(file_handler)

    # Do not propagate to root twice
    logger.propagate = False

    return logger


# Global instance
logger = configure_logging()
