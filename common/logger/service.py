# -*- coding: utf-8 -*-
"""
Defines logging service
"""
from common.logger import getLogger, configure_loglevel

_logger = getLogger("vCenterCommon")


class LoggingService(object):
    def __init__(self, log_level_console, log_level_file, filename):
        from common.utilites.io import extract_folder_name, compose_folder_if_not_existed

        log_level_file = log_level_file or log_level_console

        if filename:
            compose_folder_if_not_existed(extract_folder_name(filename))

        configure_loglevel(log_level_console, log_level_file, filename)
        _logger.info(u"Logging configured. [console:'{}' file: '{}'] Log File: '{}'".format(
            log_level_console, log_level_file, filename))


