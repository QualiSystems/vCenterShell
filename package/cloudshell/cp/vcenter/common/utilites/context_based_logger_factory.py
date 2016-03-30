from cloudshell.core.logger.qs_logger import get_qs_logger


class ContextBasedLoggerFactory(object):
    UNSUPPORTED_CONTEXT_PROVIDED = 'Unsuppported command context provided {0}'

    def create_logger_for_context(self, logger_name, context):
        """
        Create QS Logger for command context AutoLoadCommandContext or ResourceCommandContext
        :param logger_name:
        :type logger_name: str
        :param context:
        :return:
        """
        if self._is_instance_of(context, 'AutoLoadCommandContext'):
            reservation_id = 'Autoload'
            handler_name = context.resource.name
        elif self._is_instance_of(context, 'ResourceCommandContext'):
            reservation_id = context.reservation.reservation_id
            handler_name = context.resource.name
        elif self._is_instance_of(context, 'ResourceRemoteCommandContext'):
            reservation_id = context.remote_reservation.reservation_id
            handler_name = context.remote_endpoints[0].name
        else:
            raise Exception(ContextBasedLoggerFactory.UNSUPPORTED_CONTEXT_PROVIDED, context)
        logger = get_qs_logger(log_file_prefix=handler_name,
                               log_group=reservation_id,
                               log_category=logger_name)
        return logger

    @staticmethod
    def _is_instance_of(context, type_name):
        return context.__class__.__name__ == type_name
