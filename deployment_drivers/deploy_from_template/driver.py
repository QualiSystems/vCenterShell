import jsonpickle
import time
from cloudshell.api.cloudshell_api import InputNameValue
from common.cloud_shell.driver_helper import CloudshellDriverHelper
from common.model_factory import ResourceModelParser
from models.VCenterTemplateModel import VCenterTemplateModel
from models.vCenterVMFromTemplateResourceModel import vCenterVMFromTemplateResourceModel
from models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from models.DeployDataHolder import DeployDataHolder
from models.VMClusterModel import VMClusterModel


class DeployFromTemplateDriver(object):
    def __init__(self):
        self.resource_model_parser = ResourceModelParser()
        self.cs_helper = CloudshellDriverHelper()

    def Deploy(self, context, Name=None):
        """
        Deploys app from template
        :type context: models.QualiDriverModels.ResourceCommandContext
        """
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.reservation.domain)

        data_holder = self._get_data_holder(context.resource, session, Name)

        params = [InputNameValue('deploy_data', jsonpickle.encode(data_holder, unpicklable=False))]

        reservation_id = context.reservation.reservation_id
        result = session.ExecuteCommand(reservation_id,
                                        data_holder.template_model.vCenter_resource_name,
                                        "Resource",
                                        "deploy_from_template",
                                        params,
                                        False)

        return result.Output

    def _get_data_holder(self, resource, session, name):

        resource_context = resource

        # get vCenter resource name, template name, template folder
        vcenter_template_resource_model = \
            self.resource_model_parser.convert_to_resource_model(resource_context,
                                                                 vCenterVMFromTemplateResourceModel)
        vcenter_resource_model = self._get_vcenter(session, vcenter_template_resource_model.vcenter_name)
        template_model = self._create_vcenter_template_model(vcenter_resource_model, vcenter_template_resource_model,
                                                             name)
        vm_cluster_model = VMClusterModel(vcenter_resource_model.vm_cluster, vcenter_resource_model.vm_resource_pool)

        # get power state of the cloned VM
        power_on = False
        datastore_name = vcenter_template_resource_model.vm_storage

        return DeployDataHolder.create_from_params(template_model=template_model,
                                                   datastore_name=datastore_name,
                                                   vm_cluster_model=vm_cluster_model,
                                                   power_on=power_on,
                                                   ip_regex=vcenter_template_resource_model.ip_regex,
                                                   refresh_ip_timeout=vcenter_template_resource_model.refresh_ip_timeout)

    def _get_vcenter(self, api, vcenter_name):
        if not vcenter_name:
            raise ValueError('VMWare vCenter name is empty')
        vcenter_instance = api.GetResourceDetails(vcenter_name)
        vcenter_resource_model = self.resource_model_parser.convert_to_resource_model(vcenter_instance,
                                                                                      VMwarevCenterResourceModel)
        return vcenter_resource_model

    def _create_vcenter_template_model(self, vcenter_resource_model, vcenter_template_resource_model, name):
        vcenter_name = vcenter_template_resource_model.vcenter_name
        if not vcenter_name:
            raise ValueError('VCenter Name is empty')
        vm_location = vcenter_template_resource_model.vm_location or vcenter_resource_model.vm_location
        if not vm_location:
            raise ValueError('VM Location is empty')
        vcenter_template = vcenter_template_resource_model.vcenter_template or vcenter_resource_model.vcenter_template
        if not vcenter_template:
            raise ValueError('VCenter Template is empty')
        app_name = name
        if not app_name:
            raise ValueError('Name input parameter is empty')

        default_datacenter = vcenter_resource_model.default_datacenter
        if not default_datacenter:
            raise ValueError('Default Datacenter attribute on VMWare vCenter is empty')

        template_model = VCenterTemplateModel(
            vcenter_resource_name=vcenter_name,
            vm_folder=vm_location,
            template_name=vcenter_template,
            app_name=app_name,
            default_datacenter = default_datacenter
        )
        return template_model
