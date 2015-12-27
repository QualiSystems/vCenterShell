import sys
import os.path
from models.VCenterConnectionDetails import VCenterConnectionDetails
import qualipy.scripts.cloudshell_scripts_helpers as helpers

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))


class ResourceConnectionDetailsRetriever:
    def __init__(self, cs_retriever_service):
        self.csRetrieverService = cs_retriever_service

    def connection_details(self, resource_name):
        """ Retrieves connection details to vCenter from specified resource

        :param resource_name: Resource name to get connection details from
        :rtype VCenterConnectionDetails:
        """
        session = helpers.get_api_session()
        resource_details = session.GetResourceDetails(resource_name)

        # get vCenter connection details from vCenter resource
        return self.csRetrieverService.getVCenterConnectionDetails(session, resource_details)
