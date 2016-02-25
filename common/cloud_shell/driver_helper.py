import time
from cloudshell.api.cloudshell_api import CloudShellAPISession

from common.cloud_shell.data_retriever import CloudshellDataRetrieverService


class CloudshellDriverHelper(object):
    def __init__(self):
        self.cloudshell_data_retriever_service = CloudshellDataRetrieverService()
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

    def get_connection_details(self, session, vcenter_resource_model, resource):
        """
        Receives the context of the command and returns a cloudshell session
        :param CloudShellAPISession session:
        :param VMwarevCenterResourceModel vcenter_resource_model: Instance of VMwarevCenterResourceModel
        :param ResourceContextDetails resource: the context of the command
        """
        # get connection details
        connection_details = \
            self.cloudshell_data_retriever_service.get_vcenter_connection_details(
                session=session,
                vcenter_resource_model=vcenter_resource_model,
                vcenter_resource_instance=resource)

        return connection_details
