import jsonpickle
import qualipy.scripts.cloudshell_scripts_helpers as helpers
import time
from qualipy.api.cloudshell_api import *
from common.model_factory import ResourceModelParser

from models.VCenterTemplateModel import VCenterTemplateModel
from models.vCenterVMFromTemplateResourceModel import vCenterVMFromTemplateResourceModel
from models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from models.DeployDataHolder import DeployDataHolder
from models.VMClusterModel import VMClusterModel


class DeploymentServiceDriver(object):
    INPUT_KEY_COMMAND = "COMMAND"
    INPUT_KEY_DEPLOY_DATA = "deploy_data"
    COMMAND_DEPLOY_FROM_TEMPLATE = "deploy_from_template"

    def __init__(self, cs_retriever_service, resource_model_parser):
        self.cs_retriever_service = cs_retriever_service
        self.resource_model_parser = resource_model_parser

    def execute(self):
        api = helpers.get_api_session()
        data_holder = self._get_data_holder(api)
        json_data_holder = jsonpickle.encode(data_holder, unpicklable=False)

        reservation_id = helpers.get_reservation_context_details().id
        result = api.ExecuteCommand(reservation_id,
                                    data_holder.template_model.vCenter_resource_name,
                                    "Resource",
                                    self.COMMAND_DEPLOY_FROM_TEMPLATE,
                                    self._get_command_inputs_list(json_data_holder),
                                    False)

        if hasattr(result, 'Output'):
            print result.Output
        else:
            print jsonpickle.encode(result, unpicklable=False)

    def _get_data_holder(self, api):

        resource_context = helpers.get_resource_context_details()

        # get vCenter resource name, template name, template folder
        vcenter_template_resource_model = self.resource_model_parser.convert_to_resource_model(resource_context,
                                                                                vCenterVMFromTemplateResourceModel)
        vcenter_resource_model = self._get_vcenter(api, vcenter_template_resource_model.vcenter_name)
        template_model = self._create_vcenter_template_model(vcenter_resource_model, vcenter_template_resource_model)
        vm_cluster_model = VMClusterModel(vcenter_resource_model.vm_cluster, vcenter_resource_model.vm_resource_pool)

        # get power state of the cloned VM
        power_on = False  # self.cs_retriever_service.getPowerStateAttributeData(resource_context)

        # get datastore
        datastore_name = self.cs_retriever_service.getVMStorageAttributeData(resource_context)

        return DeployDataHolder.create_from_params(template_model=template_model,
                                                   datastore_name=datastore_name,
                                                   vm_cluster_model=vm_cluster_model,
                                                   power_on=power_on,
                                                   ip_regex=vcenter_template_resource_model.ip_regex)

    def _get_vcenter(self, api, vcenter_name):
        if not vcenter_name:
            raise ValueError('VMWare vCenter name is empty')
        vcenter_instance = api.GetResourceDetails(vcenter_name)
        vcenter_resource_model = self.resource_model_parser.convert_to_resource_model(vcenter_instance,
                                                                                      VMwarevCenterResourceModel)
        return vcenter_resource_model

    def _create_vcenter_template_model(self, vcenter_resource_model, vcenter_template_resource_model):
        vcenter_name = vcenter_template_resource_model.vcenter_name
        if not vcenter_name:
            raise ValueError('VCenter Name is empty')
        vm_location = vcenter_template_resource_model.vm_location or vcenter_resource_model.vm_location
        if not vm_location:
            raise ValueError('VM Location is empty')
        vcenter_template = vcenter_template_resource_model.vcenter_template or vcenter_resource_model.vcenter_template
        if not vcenter_template:
            raise ValueError('VCenter Template is empty')
        app_name = os.environ["NAME"]
        if not app_name:
            raise ValueError('NAME input parameter is empty')

        template_model = VCenterTemplateModel(
            vcenter_resource_name=vcenter_name,
            vm_folder=vm_location,
            template_name=vcenter_template,
            app_name=app_name
        )
        return template_model

    def _get_command_inputs_list(self, json_data_holder):
        return [InputNameValue(self.INPUT_KEY_DEPLOY_DATA, json_data_holder)]
