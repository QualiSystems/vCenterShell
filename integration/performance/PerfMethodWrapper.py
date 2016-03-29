from cloudshell.core.logger.qs_logger import get_qs_logger
from TimerWrapper import TimerWrapper


class PerfMethodWrapper:
    def __init__(self, action, name='', logger=None):
        self.action = action
        self.name = name
        self._print_format = '{0} ran: {1} times - total: {2} (sec) avg: {3} (sec)'

        if logger is None:
            logger = get_qs_logger('performance')
        self.logger = logger

    def run(self, i=1):
        with TimerWrapper() as t:
            for j in range(0, i):
                self.action()

        self.logger.info(self._print_format.format(self.name, i, t.secs, t.secs / i))
