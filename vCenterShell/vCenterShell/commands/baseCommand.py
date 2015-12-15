from abc import ABCMeta, abstractmethod


class baseCommand(object):
    """base command"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self): pass
