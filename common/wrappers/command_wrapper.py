import inspect

from common.cloud_shell.driver_helper import CloudshellDriverHelper
from common.model_factory import ResourceModelParser
from common.vcenter.vmomi_service import pyVmomiService
from models.VMwarevCenterResourceModel import VMwarevCenterResourceModel

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
    def __init__(self, logger, pv_service, cloud_shell_helper, resource_model_parser):
        self.pv_service = pv_service  # type: pyVmomiService
        self.logger = logger
        self.cs_helper = cloud_shell_helper  # type: CloudshellDriverHelper
        self.resource_model_parser = resource_model_parser  # type: ResourceModelParser

    def execute_command(self, command, *args):
        return self.execute_command_with_connection(None, command, *args)

    def execute_command_with_connection(self, context, command, *args):
        if not self.logger:
            print LOGGER_CANNOT_BE_NONE
            raise Exception(LOGGER_CANNOT_BE_NONE)
        if not command:
            self.logger.error(COMMAND_CANNOT_BE_NONE)
            raise Exception(COMMAND_CANNOT_BE_NONE)

        try:
            command_name = command.__name__
            logger = self.logger(command_name)
            logger.info(LOG_FORMAT.format(START, command_name))
            command_args = []
            si = None
            connection_details = None
            vc_data_model = None

            # get connection details
            if context:
                session = self.cs_helper.get_session(server_address=context.connectivity.server_address,
                                                     token=context.connectivity.admin_auth_token,
                                                     reservation_domain=context.reservation.domain)
                vc_data_model = self.resource_model_parser.convert_to_resource_model(
                        resource_instance=context.resource, resource_model_type=VMwarevCenterResourceModel)
                connection_details = self.cs_helper.get_connection_details(session=session,
                                                                           vcenter_resource_model=vc_data_model,
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

            command_args.extend(args)

            if vc_data_model and self._should_inject_vc_data_model(command):
                command_args.extend(vc_data_model)

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

    def _should_inject_vc_data_model(self, command):
        command_args = inspect.getargspec(command)[0]
        return command_args and command_args[-1] == 'vc_data_model'
