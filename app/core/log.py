import os
import sys

from loguru import logger

format = '{level} | {time:YYYY-MM-DD HH:mm:ss} | {file}:{line} - {message}'

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": format,
            "colorize": True,
            "level": "DEBUG",
        },
        {
            "sink": f"{basedir}/logs/file.log",
            "format": format,
            "retention": "2 days",
            "enqueue": True,
            "level": "INFO",
            "colorize": True,
            "encoding": "utf-8",
        }
    ]
}

logger.configure(**config)
