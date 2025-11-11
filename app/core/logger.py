import logging
import logging.config
import sys
from pathlib import Path
from app.config import settings


def setup_logging():
    """Single centralized logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "ERROR",
                    "formatter": "standard",
                    "stream": sys.stdout,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "standard",
                    "filename": "logs/error.log",
                    "maxBytes": 10485760,
                    "backupCount": 5,
                },
            },
            "loggers": {
                "": {
                    "level": "ERROR",
                    "handlers": ["console", "file"],
                },
                "uvicorn": {
                    "level": "ERROR",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    )

