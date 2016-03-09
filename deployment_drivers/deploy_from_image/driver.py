import jsonpickle
from cloudshell.api.cloudshell_api import InputNameValue
from common.cloud_shell.driver_helper import CloudshellDriverHelper
from common.model_factory import ResourceModelParser
from models.DeployDataHolder import DeployDataHolder
from models.vCenterVMFromImageResourceModel import vCenterVMFromImageResourceModel


class DeployFromImage(object):
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

        # get vCenter resource name, template name, template folder
        vcenter_image_resource_model = \
            self.resource_model_parser.convert_to_resource_model(context.resource,
                                                                 vCenterVMFromImageResourceModel)

        vcenter_res = vcenter_image_resource_model.vcenter_name

        deployment_info = self._get_deployment_info(vcenter_image_resource_model, Name)
        result = session.ExecuteCommand(context.reservation.reservation_id,
                                        vcenter_res,
                                        "Resource",
                                        "deploy_from_image",
                                        self._get_command_inputs_list(deployment_info),
                                        False)
        return result.Output

    def _get_deployment_info(self, image_model, name):
        """
        :type image_model: vCenterVMFromImageResourceModel
        """

        return DeployDataHolder({'app_name': name,
                                 'image_params': image_model
                                 })

    def _get_command_inputs_list(self, data_holder):
        return [InputNameValue('deploy_data', jsonpickle.encode(data_holder, unpicklable=False))]
