import jsonpickle
import qualipy.scripts.cloudshell_scripts_helpers as helpers
import time
from qualipy.api.cloudshell_api import *
from common.model_factory import ResourceModelParser

from models.DeployDataHolder import DeployDataHolder


class DeploymentServiceDriver(object):
    INPUT_KEY_COMMAND = "COMMAND"
    INPUT_KEY_DEPLOY_DATA = "DEPLOY_DATA"
    COMMAND_DEPLOY_FROM_TEMPLATE = "Deploy From Template"

    def __init__(self, cs_retriever_service, resource_model_parser):
        self.cs_retriever_service = cs_retriever_service
        self.resource_model_parser = resource_model_parser

    def execute(self):
        data_holder = self._get_data_holder()
        json_data_holder = jsonpickle.encode(data_holder, unpicklable=False)

        reservation_id = helpers.get_reservation_context_details().id
        api = helpers.get_api_session()
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

    def _get_data_holder(self):
        resource_context = helpers.get_resource_context_details()
        # get vCenter resource name, template name, template folder
        template_model = self.cs_retriever_service.getVCenterTemplateAttributeData(resource_context)
        # get power state of the cloned VM
        power_on = self.cs_retriever_service.getPowerStateAttributeData(resource_context)
        # get cluster and resource pool
        vm_cluster_model = self.cs_retriever_service.getVMClusterAttributeData(resource_context)
        # get datastore
        datastore_name = self.cs_retriever_service.getVMStorageAttributeData(resource_context)

        # Convert to an instance of vCenterVMFromTemplateResourceModel in order to get ip_regex
        resource_model = self.resource_model_parser.convert_to_resource_model(resource_context)
        ip_regex = resource_model.ip_regex

        deploy_data_holder = DeployDataHolder.create_from_params(template_model=template_model,
                                                                 datastore_name=datastore_name,
                                                                 vm_cluster_model=vm_cluster_model,
                                                                 power_on=power_on,
                                                                 ip_regex=ip_regex)
        return deploy_data_holder

    def _get_command_inputs_list(self, json_data_holder):
        return [InputNameValue(self.INPUT_KEY_COMMAND, "deploy_from_template"),
                InputNameValue(self.INPUT_KEY_DEPLOY_DATA, json_data_holder)]
