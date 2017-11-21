import inspect
from threading import Lock

from retrying import retry

from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService, VCenterAuthError
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.cp.vcenter.common.cloud_shell.conn_details_retriever import ResourceConnectionDetailsRetriever

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


def retry_if_auth_error(ex):
    return isinstance(ex, VCenterAuthError)


class CommandWrapper:
    def __init__(self, pv_service, resource_model_parser, context_based_logger_factory):
        """

        :param pv_service:
        :param cloud_shell_helper:
        :param resource_model_parser:
        :param context_based_logger_factory:
        :type context_based_logger_factory: cloudshell.cp.vcenter.common.utilites.context_based_logger_factory.ContextBasedLoggerFactory
        :return:
        """
        self.pv_service = pv_service  # type: pyVmomiService
        self.resource_model_parser = resource_model_parser  # type: ResourceModelParser
        self.context_based_logger_factory = context_based_logger_factory  # type ContextBasedLoggerFactory
        # add lock
        self.lock = Lock()
        self.si = None
        self.connection_details = None

    @retry(stop_max_attempt_number=3, wait_fixed=2000, retry_on_exception=retry_if_auth_error)
    def execute_command_with_connection(self, context, command, *args):
        """
        Note: session & vcenter_data_model & reservation id objects will be injected dynamically to the command
        :param command:
        :param context: instance of ResourceCommandContext or AutoLoadCommandContext
        :type context: cloudshell.shell.core.context.ResourceCommandContext
        :param args:
        """

        logger = self.context_based_logger_factory.create_logger_for_context(
                logger_name='vCenterShell',
                context=context)

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
                with CloudShellSessionContext(context) as cloudshell_session:
                    session = cloudshell_session

                vcenter_data_model = self.resource_model_parser.convert_to_vcenter_model(context.resource)
                connection_details = ResourceConnectionDetailsRetriever.get_connection_details(session=session,
                                                                           vcenter_resource_model=vcenter_data_model,
                                                                           resource_context=context.resource)

            if connection_details:
                logger.info(INFO_CONNECTING_TO_VCENTER.format(connection_details.host))
                logger.debug(
                        DEBUG_CONNECTION_INFO.format(connection_details.host,
                                                     connection_details.username,
                                                     connection_details.port))

                si = self.get_py_service_connection(connection_details, logger)
            if si:
                logger.info(CONNECTED_TO_CENTER.format(connection_details.host))
                command_args.append(si)

            self._try_inject_arg(command=command,
                                 command_args=command_args,
                                 arg_object=session,
                                 arg_name='session')
            self._try_inject_arg(command=command,
                                 command_args=command_args,
                                 arg_object=vcenter_data_model,
                                 arg_name='vcenter_data_model')
            self._try_inject_arg(command=command,
                                 command_args=command_args,
                                 arg_object=self._get_reservation_id(context),
                                 arg_name='reservation_id')
            self._try_inject_arg(command=command,
                                 command_args=command_args,
                                 arg_object=logger,
                                 arg_name='logger')

            command_args.extend(args)

            logger.info(EXECUTING_COMMAND.format(command_name))
            logger.debug(DEBUG_COMMAND_PARAMS.format(COMMA.join([str(x) for x in command_args])))

            results = command(*tuple(command_args))

            logger.info(FINISHED_EXECUTING_COMMAND.format(command_name))
            logger.debug(DEBUG_COMMAND_RESULT.format(str(results)))

            return results
        except Exception:
            logger.exception(COMMAND_ERROR.format(command_name))
            raise
        finally:
            logger.info(LOG_FORMAT.format(END, command_name))

    def get_py_service_connection(self, req_connection_details, logger):
        logger.info("get_py_service_connection")
        if self.si is None or self.has_connection_details_changed(req_connection_details):
            with self.lock:
                if self.si is None or self.has_connection_details_changed(req_connection_details):
                    logger.info("Creating a new connection.")
                    self.si = self.pv_service.connect(req_connection_details.host,
                                                      req_connection_details.username,
                                                      req_connection_details.password,
                                                      req_connection_details.port)
                    self.connection_details = req_connection_details
        return self.si

    def has_connection_details_changed(self, req_connection_details):
        """
        :param cloudshell.cp.vcenter.models.VCenterConnectionDetails.VCenterConnectionDetails req_connection_details:
        :return:
        """
        if self.connection_details is None and req_connection_details is None:
            return False
        if self.connection_details is None or req_connection_details is None:
            return True
        return not all([self.connection_details.host == req_connection_details.host,
                        self.connection_details.username == req_connection_details.username,
                        self.connection_details.password == req_connection_details.password,
                        self.connection_details.port == req_connection_details.port])

    @staticmethod
    def _get_domain(context):
        # noinspection PyBroadException
        domain = 'Global'
        reservation = getattr(context, 'reservation', getattr(context, 'remote_reservation', None))
        if reservation:
            domain = reservation.domain
        return domain

    @staticmethod
    def _get_reservation_id(context):
        reservation_id = None
        reservation = getattr(context, 'reservation', getattr(context, 'remote_reservation', None))
        if reservation:
            reservation_id = reservation.reservation_id
        return reservation_id

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
