import inspect

from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from cloudshell.shell.core.driver_context import ResourceCommandContext, AutoLoadCommandContext

UNSUPPORTED_CONTEXT_PROVIDED = 'Unsuppported command context provided {0}'

DISCONNCTING_VCENERT = 'disconnecting from vcenter: {0}'
COMMAND_ERROR = 'error has occurred while executing command: {0}'
DEBUG_COMMAND_RESULT = 'finished executing with the result: {0}'
FINISHED_EXECUTING_COMMAND = 'finished executing command: {0}'
DEBUG_COMMAND_PARAMS = 'command params: {0}'
COMMA = ','
EXECUTING_COMMAND = 'executing command: {0}'
CONNECTED_TO_CENTER = 'connected to vcenter: {0}'
DEBUG_CONNECTION_INFO = 'connection params: host: {0} username: {1} port: {2}'
LOGGER_CANNOT_BE_NONE = 'logger cannot be None'
COMMAND_CANNOT_BE_NONE = 'command cannot be None'
INFO_CONNECTING_TO_VCENTER = 'connecting to vcenter: {0}'
START = 'START'
END = 'END'
LOG_FORMAT = 'action:{0} command_name:{1}'


class CommandWrapper:
    def __init__(self, pv_service, cloud_shell_helper, resource_model_parser):
        """

        :param pv_service:
        :param cloud_shell_helper:
        :param resource_model_parser:
        :return:
        """
        self.pv_service = pv_service  # type: pyVmomiService
        self.cs_helper = cloud_shell_helper  # type: CloudshellDriverHelper
        self.resource_model_parser = resource_model_parser  # type: ResourceModelParser

    def execute_command_with_connection(self, context, command, *args):
        """
        Note: session & vcenter_data_model objects will be injected dynamically to the command
        :param command:
        :param context: instance of ResourceCommandContext or AutoLoadCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :param args:
        """

        logger = self._create_logger_for_context(context)

        if not command:
            logger.error(COMMAND_CANNOT_BE_NONE)
            raise Exception(COMMAND_CANNOT_BE_NONE)

        try:
            command_name = command.__name__
            logger.info(LOG_FORMAT.format(START, command_name))
            command_args = []
            si = None
            session = None
            connection_details = None
            vcenter_data_model = None

            # get connection details
            if context:
                session = self.cs_helper.get_session(server_address=context.connectivity.server_address,
                                                     token=context.connectivity.admin_auth_token,
                                                     reservation_domain=self._get_domain(context))
                vcenter_data_model = self.resource_model_parser.convert_to_resource_model(
                    resource_instance=context.resource, resource_model_type=VMwarevCenterResourceModel)
                connection_details = self.cs_helper.get_connection_details(session=session,
                                                                           vcenter_resource_model=vcenter_data_model,
                                                                           resource_context=context.resource)

            if connection_details:
                logger.info(INFO_CONNECTING_TO_VCENTER.format(connection_details.host))
                logger.debug(
                    DEBUG_CONNECTION_INFO.format(connection_details.host,
                                                 connection_details.username,
                                                 connection_details.port))

                si = self.pv_service.connect(connection_details.host,
                                             connection_details.username,
                                             connection_details.password,
                                             connection_details.port)
            if si:
                logger.info(CONNECTED_TO_CENTER.format(connection_details.host))
                command_args.append(si)

            self._try_inject_arg(command=command, command_args=command_args, arg_object=session, arg_name='session')
            self._try_inject_arg(command=command, command_args=command_args, arg_object=vcenter_data_model,
                                 arg_name='vcenter_data_model')
            self._try_inject_arg(command=command, command_args=command_args, arg_object=logger,
                                 arg_name='logger')

            command_args.extend(args)

            logger.info(EXECUTING_COMMAND.format(command_name))
            logger.debug(DEBUG_COMMAND_PARAMS.format(COMMA.join([str(x) for x in command_args])))

            results = command(*tuple(command_args))

            if not results:
                results = 'finished successfully'

            logger.info(FINISHED_EXECUTING_COMMAND.format(command_name))
            logger.debug(DEBUG_COMMAND_RESULT.format(str(results)))

            return results
        except Exception as e:
            logger.error(COMMAND_ERROR.format(command_name))
            logger.exception(e)
            raise
        finally:
            if si:
                logger.info(DISCONNCTING_VCENERT.format(connection_details.host))
                self.pv_service.disconnect(si)
            logger.info(LOG_FORMAT.format(END, command_name))

    @staticmethod
    def _create_logger_for_context(context):
        if isinstance(context, AutoLoadCommandContext):
            reservation_id = 'Autoload'
            handler_name = 'Default'
        elif isinstance(context, ResourceCommandContext) or \
                (hasattr(context, 'reservation') and hasattr(context.reservation, 'reservation_id')):
            reservation_id = context.reservation.reservation_id
            handler_name = context.resource.name
        else:
            raise Exception(UNSUPPORTED_CONTEXT_PROVIDED, type(context))
        logger = get_qs_logger(name='vCenterShell',
                               handler_name=handler_name,
                               reservation_id=reservation_id)
        return logger

    @staticmethod
    def _get_domain(context):
        # noinspection PyBroadException
        try:
            return context.remote_reservation.domain
        except:
            return context.reservation.domain

    def _try_inject_arg(self, command, command_args, arg_object, arg_name):
        try:
            if not arg_object:
                return

            command_args_spec = self._get_command_args(command)
            if not command_args:
                return

            index = command_args_spec.index(arg_name)
            if index >= 0:
                command_args.insert(index, arg_object)
        except:
            pass

    def _get_command_args(self, command):
        command_args = inspect.getargspec(command)[0]
        if command_args and command_args[0] == 'self':
            command_args.pop(0)
        return command_args
