# -*- coding: utf-8 -*-

"""
Very much common Input/Output Utils
"""

import os.path


def extract_folder_name(whole_path):
    if whole_path:
        folder, name = os.path.split(whole_path)
        return folder
    return None


def compose_folder_if_not_existed(whole_path):
    if whole_path and not os.path.exists(whole_path):
        return None
        # os.makedirs(whole_path)
        # _logger.debug(u"Folder composed: '{}'".format(whole_path))
    return whole_path


def get_path_and_name(full_name):
    """
    Split Whole Patch onto 'Patch' and 'Name'
    :param full_name: <str> Full Resource Name - likes 'Root/Folder/Folder2/Name'
    :return: tuple (Patch, Name)
    """
    if full_name:
        parts = full_name.split("/")
        return ("/".join(parts[0:-1]), parts[-1]) if len(parts) > 1 else ("/", full_name)
    return None, None
