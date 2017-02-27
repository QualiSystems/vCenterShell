import jsonpickle
from cloudshell.api.cloudshell_api import InputNameValue, CommandExecutionCancelledResultInfo
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

from cloudshell.cp.vcenter.models.DeployDataHolder import DeployDataHolder
from cloudshell.cp.vcenter.models.vCenterVMFromImageResourceModel import vCenterVMFromImageResourceModel

from cloudshell.cp.vcenter.common.cloud_shell.driver_helper import CloudshellDriverHelper
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser


class DeployFromImage(ResourceDriverInterface):
    def cleanup(self):
        pass

    def __init__(self):
        self.cs_helper = CloudshellDriverHelper()
        self.resource_model_parser = ResourceModelParser()

    def initialize(self, context):
        pass

    def Deploy(self, context, Name=None):
        """
        Deploys app from image
        :type context: models.QualiDriverModels.ResourceCommandContext
        """
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.reservation.domain)

        app_request = jsonpickle.decode(context.resource.app_context.app_request_json)

        if not Name:
            Name = app_request['name']

        # Cloudshell >= v7.2 have no vCenter Name attribute, fill it from the cloudProviderName context attr
        cloud_provider_name = app_request["deploymentService"].get("cloudProviderName")

        if cloud_provider_name:
            attrs = self.resource_model_parser.get_resource_attributes(context.resource)
            attrs["vCenter Name"] = cloud_provider_name

        # get vCenter resource name, template name, template folder
        vcenter_image_resource_model = \
            self.resource_model_parser.convert_to_resource_model(context.resource,
                                                                 vCenterVMFromImageResourceModel)

        vcenter_res = vcenter_image_resource_model.vcenter_name


        deployment_info = self._get_deployment_info(vcenter_image_resource_model, Name)

        reservation_id = context.reservation.reservation_id
        result = session.ExecuteCommand(context.reservation.reservation_id,
                                        vcenter_res,
                                        "Resource",
                                        "deploy_from_image",
                                        self._get_command_inputs_list(deployment_info),
                                        False)

        return self.cs_helper.proceed_command_execution_result(reservation_id=reservation_id, result=result,
                                                               context=context)

    def _get_deployment_info(self, image_model, name):
        """
        :type image_model: vCenterVMFromImageResourceModel
        """

        return DeployDataHolder({'app_name': name,
                                 'image_params': image_model
                                 })

    def _get_command_inputs_list(self, data_holder):
        return [InputNameValue('deploy_data', jsonpickle.encode(data_holder, unpicklable=False))]
