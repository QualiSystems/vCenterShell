from cloudshell.cp.vcenter.models.VCenterConnectionDetails import VCenterConnectionDetails


class ResourceConnectionDetailsRetriever:

    @staticmethod
    def get_connection_details(session, vcenter_resource_model, resource_context):
        """
        Methods retrieves the connection details from the vcenter resource model attributes.

        :param CloudShellAPISession session:
        :param VMwarevCenterResourceModel vcenter_resource_model: Instance of VMwarevCenterResourceModel
        :param ResourceContextDetails resource_context: the context of the command
        """

        session = session
        resource_context = resource_context

        # get vCenter connection details from vCenter resource
        user = vcenter_resource_model.user
        vcenter_url = resource_context.address
        password = session.DecryptPassword(vcenter_resource_model.password).Value

        return VCenterConnectionDetails(vcenter_url, user, password)

