import jsonpickle
from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.vcenter.models.VCenterDeployVMFromLinkedCloneResourceModel import VCenterDeployVMFromLinkedCloneResourceModel

from cloudshell.cp.vcenter.common.cloud_shell.driver_helper import CloudshellDriverHelper
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface


class DeployCloneFromVMDriver(ResourceDriverInterface):
    def __init__(self):
        self.resource_model_parser = ResourceModelParser()
        self.cs_helper = CloudshellDriverHelper()

    def cleanup(self):
        pass

    def initialize(self, context):
        pass

    def Deploy(self, context, Name=None):
        """
        Deploys app from template
        :type context: models.QualiDriverModels.ResourceCommandContext
        :param Name: Name of the Deployment
        :type Name: str
        :rtype: str
        """
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.reservation.domain)

        vcenter_template_resource_model = \
            self.resource_model_parser.convert_to_resource_model(context.resource,
                                                                 vCenterCloneFromVMResourceModel)

        if not Name:
            Name = jsonpickle.decode(context.resource.app_context.app_request_json)['name']

        deploy_from_template_details = DeployFromTemplateDetails(vcenter_template_resource_model, Name)

        params = [InputNameValue('deploy_data', jsonpickle.encode(deploy_from_template_details, unpicklable=False))]

        reservation_id = context.reservation.reservation_id
        result = session.ExecuteCommand(reservation_id,
                                        vcenter_template_resource_model.vcenter_name,
                                        "Resource",
                                        "deploy_clone_from_vm",
                                        params,
                                        False)

        return result.Output
