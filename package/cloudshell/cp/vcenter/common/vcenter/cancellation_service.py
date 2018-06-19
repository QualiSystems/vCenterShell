class CancellationException(Exception):
    """Raised when command was cancelled from the CloudShell"""

    def __init__(self, message, data):
        """
        :param str message:
        :param dict data:
        :return:
        """
        # Call the base class constructor with the parameters it needs
        super(CancellationException, self).__init__(message)

        self.data = data if data else {}


class CommandCancellationService(object):
    def check_if_cancelled(self, cancellation_context, data=None):
        """Check if command was cancelled from the CloudShell

        :param cancellation_context cloudshell.shell.core.driver_context.CancellationContext instance
        :param dict data: Dictionary that will be added to the cancellation exception if raised.
                          Use this container to add context data to the cancellation exception to be used
                          by the exception handler
        :raises cloudshell.cp.azure.common.exceptions.cancellation_exception.CancellationException
        :return:
        """
        if cancellation_context and cancellation_context.is_cancelled:
            return True
