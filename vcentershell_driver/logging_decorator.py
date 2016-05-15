import functools
import inspect
from cloudshell.cp.vcenter.common.utilites.context_based_logger_factory import ContextBasedLoggerFactory

CONTEXT = "context"


class LoggingDecorator(object):
    """
    Decorates invocation of a method by initializing a logger and injecting it into logger property of context
     argument
    """
    def __call__(self, func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if CONTEXT in kwargs:
                context = kwargs[CONTEXT]
            else:
                command_args = LoggingDecorator._get_command_args(func)
                context = command_args[CONTEXT]

            context.logger = ContextBasedLoggerFactory().create_logger_for_context('vCenterShell', context)
            f_result = func(*args, **kwargs)

            return f_result

        return wrapper

    @staticmethod
    def _get_command_args(command):
        """
        Returns list of arguments of a function or method
        :param command: Method to analyze
        :return: list of arguments
        """
        command_args = inspect.getargspec(command)[0]
        if command_args and command_args[0] == 'self':
            command_args.pop(0)
        return command_args


