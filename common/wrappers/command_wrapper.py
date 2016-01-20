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
    def __init__(self, logger, pv_service):
        self.pv_service = pv_service
        self.logger = logger

    def execute_command(self, command, *args):
        return self.execute_command_with_connection(None, command, *args)

    def execute_command_with_connection(self, connection_details, command, *args):
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

            logger.info(EXECUTING_COMMAND.format(command_name))
            logger.debug(DEBUG_COMMAND_PARAMS.format(COMMA.join([str(x) for x in command_args])))

            results = command(*tuple(command_args))

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
