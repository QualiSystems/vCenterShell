from qualipy.api.cloudshell_api import CloudShellAPISession

from common.cloudshell.data_retriever import CloudshellDataRetrieverService


class CloudshellDriverHelper(object):
    def __init__(self):
        self.cloudshell_data_retriever_service = CloudshellDataRetrieverService()
        self.session_class = CloudShellAPISession

    def get_session(self, context):
        """
        gets the current session

        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :return CloudShellAPISession
        """

        return self.session_class(host=context.connectivity.serverAddress,
                                  token=context.connectivity.adminAuthToken,
                                  user='admin',  # Todo: remove this
                                  password='admin',  # Todo: remove this
                                  domain=context.reservation.domain)

    def get_connection_details(self, session, context):
        """
        Receives the context of the command and returns a cloudshell session
        :param CloudShellAPISession session:
        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        """
        # get connection details
        connection_details = \
            self.cloudshell_data_retriever_service.getVCenterConnectionDetails(session=session,
                                                                               vCenter_resource_details=context.resource)
        return connection_details
