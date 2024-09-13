import logging
import logging.config
import os

log_level = os.environ.get("PF_LOG_LEVEL", "INFO")

def init():
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] [%(processName)s/%(threadName)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "console": {
                "level": log_level,
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Default is stderr
            },
        },
        "loggers": {
            "": {  # root logger
                "level": "INFO",
                "handlers": ["console"],
                "propagate": True,
            },
            "uvicorn.error": {
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console"],
            },
            "uvicorn.access": {
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console"],
            },
            "tensorflow": {
                "level": "DEBUG",
                "propagate": True,
                "handlers": ["console"],
            },
            "peewee": {
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console"],
            },
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)