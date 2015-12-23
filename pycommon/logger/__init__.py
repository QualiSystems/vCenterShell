# -*- coding: utf-8 -*-

"""
Logger provider.
Initial Log Level defined with 'LOG_LEVEL' variable (default value == 'DEBUG')

"""

import os
import logging
from logging.config import fileConfig


def get_logging_config(level_console="DEBUG", level_file=None, logfile=None):
    """
    Returns Logging Config
    @see https://docs.python.org/2/library/logging.config.html#logging.config.dictConfig
    :param level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    :return: <dict> logging config depends on 'log level'
    """
    level_file = level_file or level_console
    logger = {
        'version': 1,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
                'datefmt': "%d/%b/%Y %H:%M:%S"
            },
            'simple': {
                'format': '%(asctime)s %(levelname)s %(message)s',
                'datefmt': "%d/%b/%Y %H:%M:%S"
            },
        },
        'disable_existing_loggers': False,

        'handlers': {
            'console': {
                'level': level_console,
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'] if logfile else ['console'],
                'level': 'DEBUG',
                'propagate': True
            },
            'vCenterShell': {
                'handlers': ['console', 'file'] if logfile else ['console'],
                'level': 'DEBUG',
                'propagate': True
            },
            'vCenterCommon': {
                'handlers': ['console', 'file'] if logfile else ['console'],
                'level': 'DEBUG',
                'propagate': True
            },
        }
    }
    if logfile:
        logger["handlers"]["file"] = {
                'level': level_file,
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': logfile,
                'maxBytes': 1024 * 10,
                'backupCount': 10,
                'formatter': 'simple'
                }
    return logger


initial_log_level = os.environ.get("LOGGING_LEVEL") or "DEBUG"
logging.config.dictConfig(get_logging_config(initial_log_level))


def configure_loglevel(level_console="DEBUG", level_file=None, logfile=None):
    logging.config.dictConfig(get_logging_config(level_console, level_file, logfile))


def getLogger(name):
    logger = logging.getLogger(name)
    return logger
