import sys
import os.path
from models.VCenterConnectionDetails import VCenterConnectionDetails
import qualipy.scripts.cloudshell_scripts_helpers as helpers

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))


class ResourceConnectionDetailsRetriever:
    def __init__(self, qualipy_helpers, cs_retriever_service):
        self.qualipy_helpers = qualipy_helpers
        self.csRetrieverService = cs_retriever_service

    def connection_details(self):
        """ Retrieves connection details to vCenter from specified resource

        :param resource_name: Resource name to get connection details from
        :rtype VCenterConnectionDetails:
        """
        # gets the name of the vcenter to connect
        resource_att = self.qualipy_helpers.get_resource_context_details()
        inventory_path_data = self.connection_retriever.getVCenterInventoryPathAttributeData(resource_att)
        vcenter_resource_name = inventory_path_data['vCenter_resource_name']

        session = helpers.get_api_session()
        resource_details = session.GetResourceDetails(vcenter_resource_name)

        # get vCenter connection details from vCenter resource
        return self.csRetrieverService.getVCenterConnectionDetails(session, resource_details)
