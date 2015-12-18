"""
Logger provider.
"""

import os
import logging
from logging.config import fileConfig

path = os.path.join(os.path.dirname(__file__), "logging.config")
logging.config.fileConfig(path)


def getLogger(name):
    logger = logging.getLogger(name)
    return logger


