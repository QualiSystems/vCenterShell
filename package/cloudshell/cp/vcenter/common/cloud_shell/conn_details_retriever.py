from cloudshell.cp.vcenter.models.VCenterConnectionDetails import VCenterConnectionDetails


class ResourceConnectionDetailsRetriever:
    def __init__(self, qualipy_helpers):
        """
        :param qualipy.scripts.cloudshell_scripts_helpers qualipy_helpers:
        :param cs_retriever_service:
        :return:
        """
        self.qualipy_helpers = qualipy_helpers

    def connection_details(self):
        """ Retrieves connection details to vCenter from specified resource

        :param resource_name: Resource name to get connection details from
        :rtype VCenterConnectionDetails:
        """
        # gets the vcenter resource context to connect. We assume this will only run on a cloud prodvider resource
        session = self.qualipy_helpers.get_api_session()
        resource_context = self.qualipy_helpers.get_resource_context_details()

        # get vCenter connection details from vCenter resource
        user = resource_context.attributes["User"]
        encrypted_pass = resource_context.attributes["Password"]
        vcenter_url = resource_context.address
        password = session.DecryptPassword(encrypted_pass).Value

        return VCenterConnectionDetails(vcenter_url, user, password)
