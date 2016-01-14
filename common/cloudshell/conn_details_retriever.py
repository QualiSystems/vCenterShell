

class ResourceConnectionDetailsRetriever:
    def __init__(self, qualipy_helpers, cs_retriever_service):
        """
        :param qualipy.scripts.cloudshell_scripts_helpers qualipy_helpers:
        :param cs_retriever_service:
        :return:
        """
        self.qualipy_helpers = qualipy_helpers
        self.csRetrieverService = cs_retriever_service

    def connection_details(self):
        """ Retrieves connection details to vCenter from specified resource

        :param resource_name: Resource name to get connection details from
        :rtype VCenterConnectionDetails:
        """
        # gets the vcenter resource context to connect. We assume this will only run on a cloud prodvider resource
        session = self.qualipy_helpers.get_api_session()
        resource_context = self.qualipy_helpers.get_resource_context_details()

        # get vCenter connection details from vCenter resource
        return self.csRetrieverService.getVCenterConnectionDetails(session, resource_context)
