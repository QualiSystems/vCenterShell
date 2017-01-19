from cloudshell.api.cloudshell_api import CloudShellAPISession, CommandExecutionCancelledResultInfo

from cloudshell.cp.vcenter.common.utilites.context_based_logger_factory import ContextBasedLoggerFactory
from cloudshell.cp.vcenter.models.VCenterConnectionDetails import VCenterConnectionDetails


class CloudshellDriverHelper(object):
    def __init__(self):
        self.session_class = CloudShellAPISession

    def get_session(self, server_address, token, reservation_domain):
        """
        gets the current session

        :param str reservation_domain: reservation domain
        :param token: the admin authentication token
        :param server_address: cloudshell server address
        :return CloudShellAPISession
        """
        return self.session_class(host=server_address,
                                  token_id=token,
                                  username=None,
                                  password=None,
                                  domain=reservation_domain)

    def get_connection_details(self, session, vcenter_resource_model, resource_context):
        """
        Methods retrieves the connection details from the vcenter resource model attributes.

        :param CloudShellAPISession session:
        :param VMwarevCenterResourceModel vcenter_resource_model: Instance of VMwarevCenterResourceModel
        :param ResourceContextDetails resource_context: the context of the command
        """

        # get connection details
        user = vcenter_resource_model.user
        encrypted_pass = vcenter_resource_model.password
        vcenter_url = resource_context.address
        password = session.DecryptPassword(encrypted_pass).Value

        return VCenterConnectionDetails(vcenter_url, user, password)

    def proceed_command_execution_result(self, reservation_id, result, context):
        if isinstance(result, CommandExecutionCancelledResultInfo):
            logger_factory = ContextBasedLoggerFactory()
            logger = logger_factory.create_logger_for_context(logger_name='vCenterShell',
                                                              context=context)
            logger.info("Deploy from template for reservation '{0}': {1}".format(reservation_id, result.Message))
            return result.Message
        else:
            return result.Output

