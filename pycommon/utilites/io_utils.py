# -*- coding: utf-8 -*-

"""
Very much common Input/Output Utils
"""

import os.path

from pycommon.logger import getLogger
_logger = getLogger("vCenterCommon")


def extract_folder_name(whole_path):
    if whole_path:
        folder, name = os.path.split(whole_path)
        return folder
    return None


def compose_folder_if_not_existed(whole_path):
    if whole_path and not os.path.exists(whole_path):
        os.makedirs(whole_path)
        _logger.debug(u"Folder composed: '{}'".format(whole_path))
