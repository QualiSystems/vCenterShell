import time
from qualipy.api.cloudshell_api import CloudShellAPISession

from common.cloudshell.data_retriever import CloudshellDataRetrieverService


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
                                  token=token,
                                  user=None,
                                  password=None,
                                  domain=reservation_domain)

    def get_connection_details(self, session, resource):
        """
        Receives the context of the command and returns a cloudshell session
        :param CloudShellAPISession session:
        :param ResourceContextDetails resource: the context of the command
        :type context: models.QualiDriverModels.ResourceRemoteCommandContext or models.QualiDriverModels.ResourceCommandContext
        """
        # get connection details
        connection_details = \
            self.cloudshell_data_retriever_service.getVCenterConnectionDetails(session=session,
                                                                               vCenter_resource_details=resource)
        return connection_details
