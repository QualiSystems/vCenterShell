# -*- coding: utf-8 -*-
"""
Defines logging service
"""
from vCenterShell.pycommon.logger import getLogger, configure_loglevel

_logger = getLogger("vCenterCommon")

DEFAULT_LOG_FILE = "./logs/vCenterShell.log"


class LoggingService(object):
    def __init__(self, log_level_console, log_level_file=None, filename=DEFAULT_LOG_FILE):
        log_level_file = log_level_file or log_level_console
        configure_loglevel(log_level_console, log_level_file, filename)
        _logger.info(u"Logging configured. [console:'{}' file: '{}'] Log File: '{}'".format(
            log_level_console, log_level_file, filename))
