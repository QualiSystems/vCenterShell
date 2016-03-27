from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.shell.core.driver_context import AutoLoadCommandContext, ResourceCommandContext


class ContextBasedLoggerFactory(object):
    UNSUPPORTED_CONTEXT_PROVIDED = 'Unsuppported command context provided {0}'

    @staticmethod
    def create_logger_for_context(context):
        """
        Create QS Logger for command context AutoLoadCommandContext or ResourceCommandContext
        :param context:
        :return:
        """
        if isinstance(context, AutoLoadCommandContext):
            reservation_id = 'Autoload'
            handler_name = 'Default'
        elif isinstance(context, ResourceCommandContext) or \
                (hasattr(context, 'reservation') and hasattr(context.reservation, 'reservation_id')):
            reservation_id = context.reservation.reservation_id
            handler_name = context.resource.name
        else:
            raise Exception(ContextBasedLoggerFactory.UNSUPPORTED_CONTEXT_PROVIDED, type(context))
        logger = get_qs_logger(name='vCenterShell',
                               handler_name=handler_name,
                               reservation_id=reservation_id)
        return logger
