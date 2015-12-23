# -*- coding: utf-8 -*-

from vCenterShell.pycommon.logger import getLogger
_logger = getLogger("vCenterCommon")


class NamedEntry(object):
    """
    Defines abstract named entry
    """
    def __init__(self, entry_name):
        """
        :param entry_name: <str> name of entry
        """
        self.name = entry_name




