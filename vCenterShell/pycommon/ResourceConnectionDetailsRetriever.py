import sys
import os.path
from models.VCenterConnectionDetails import VCenterConnectionDetails
import qualipy.scripts.cloudshell_scripts_helpers as helpers

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))


class ResourceConnectionDetailsRetriever:

    def __init__(self, cs_retriever_service):
        self.csRetrieverService = cs_retriever_service

    def get_connection_details(self, resource_name):
        """
        :rtype VCenterConnectionDetails:
        """
        session = helpers.get_api_session()
        vCenter_details = session.GetResourceDetails(resource_name)

        # get vCenter connection details from vCenter resource
        vCenterConn = self.csRetrieverService.getVCenterConnectionDetails(session, vCenter_details)

        return VCenterConnectionDetails(vCenterConn["vCenter_url"], vCenterConn["user"], vCenterConn["password"])
