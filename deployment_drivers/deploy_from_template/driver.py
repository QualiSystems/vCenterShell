import jsonpickle
from cloudshell.api.cloudshell_api import InputNameValue
from vCenterShell.models.vCenterVMFromTemplateResourceModel import vCenterVMFromTemplateResourceModel

from vCenterShell.common.cloud_shell.driver_helper import CloudshellDriverHelper
from vCenterShell.common.model_factory import ResourceModelParser
from vCenterShell.models.DeployFromTemplateDetails import DeployFromTemplateDetails


class DeployFromTemplateDriver(object):
    def __init__(self):
        self.resource_model_parser = ResourceModelParser()
        self.cs_helper = CloudshellDriverHelper()

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
                                                                 vCenterVMFromTemplateResourceModel)

        deploy_from_template_details = DeployFromTemplateDetails(vcenter_template_resource_model, Name)

        params = [InputNameValue('deploy_data', jsonpickle.encode(deploy_from_template_details, unpicklable=False))]

        reservation_id = context.reservation.reservation_id
        result = session.ExecuteCommand(reservation_id,
                                        vcenter_template_resource_model.vcenter_name,
                                        "Resource",
                                        "deploy_from_template",
                                        params,
                                        False)

        return result.Output
