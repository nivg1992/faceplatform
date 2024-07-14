import logging
import logging.config

def init():
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] [%(processName)s/%(threadName)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
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