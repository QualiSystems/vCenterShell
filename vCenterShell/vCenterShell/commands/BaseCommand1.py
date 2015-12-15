from abc import ABCMeta, abstractmethod


class BaseCommand1(object):
    """base command"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self): pass
