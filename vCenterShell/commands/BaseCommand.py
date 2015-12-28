﻿from abc import ABCMeta, abstractmethod


class BaseCommand(object):
    """base command"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self):
        """This method should be overridden"""
