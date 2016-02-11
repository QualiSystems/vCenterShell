import unittest

from mock import Mock, MagicMock

from common.cloudshell.data_retriever import *
from deployment_service.driver import *

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))


class test_DeploymentService(unittest.TestCase):
    def test_get_data_holder_in_deployment_service(self):
        cs = Mock()
        cs.getVCenterTemplateAttributeData = Mock(return_value=VCenterTemplateModel("vCenter", "some_folder",
                                                                                    "vm_template"))
        cs.getPowerStateAttributeData = Mock(return_value=True)
        cs.getVMClusterAttributeData = Mock(return_value=VMClusterModel("some_cluster", "some_resource_pool"))
        cs.getVMStorageAttributeData = Mock(return_value="some_datastore")

        deploymentService = DeploymentServiceDriver(cs)

        helpers.get_resource_context_details = Mock()

        os.environ["NAME"] = "app name"

        data_holder = deploymentService._get_data_holder()

        self.assertEquals(data_holder.template_model.vCenter_resource_name, "vCenter")
        self.assertEquals(data_holder.template_model.vm_folder, "some_folder")
        self.assertEquals(data_holder.template_model.template_name, "vm_template")

        self.assertEquals(data_holder.datastore_name, "some_datastore")

        self.assertEquals(data_holder.vm_cluster_model.cluster_name, "some_cluster")
        self.assertEquals(data_holder.vm_cluster_model.resource_pool, "some_resource_pool")

        self.assertFalse(data_holder.power_on)

    def test_execute_deployment_service(self):
        session = Mock()
        session.ExecuteCommand = MagicMock(return_value=Mock(Output="jsonresult"))

        reservation_details = Mock()
        reservation_details.id = "3c4b9463-a722-4a63-9c9a-464da6d1e84b"

        helpers.get_reservation_context_details = Mock(return_value=reservation_details)
        helpers.get_api_session = Mock(return_value=session)

        template_model = VCenterTemplateModel("vCenter", "some_folder", "vm_template")
        vm_cluster_model = VMClusterModel("some_cluster", "some_resource_pool")
        data_holder = DeployDataHolder.create_from_params(template_model=template_model,
                                                          datastore_name="some_datastore",
                                                          vm_cluster_model=vm_cluster_model,
                                                          power_on=True)
        json_data_holder = jsonpickle.encode(data_holder, unpicklable=False)

        command_inputs = [InputNameValue(DeploymentServiceDriver.INPUT_KEY_COMMAND, "deploy_from_template"),
                          InputNameValue(DeploymentServiceDriver.INPUT_KEY_DEPLOY_DATA, json_data_holder)]

        cs = Mock()
        deploymentService = DeploymentServiceDriver(cs)
        deploymentService._get_data_holder = Mock(return_value=data_holder)
        deploymentService._get_command_inputs_list = Mock(return_value=command_inputs)

        deploymentService.execute()

        session.ExecuteCommand.assert_called_with(reservation_details.id,
                                                  data_holder.template_model.vCenter_resource_name,
                                                  "Resource",
                                                  DeploymentServiceDriver.COMMAND_DEPLOY_FROM_TEMPLATE,
                                                  command_inputs,
                                                  False)

    def test_get_command_inputs_list(self):
        json_data = '{"key1":"value1"}'

        cs = Mock()
        deployment_service = DeploymentServiceDriver(cs)
        command_inputs = deployment_service._get_command_inputs_list(json_data)

        self.assertEquals(len(command_inputs), 1)
        self.assertEquals(command_inputs[0].Value, json_data)
        self.assertEquals(command_inputs[0].Name, DeploymentServiceDriver.INPUT_KEY_DEPLOY_DATA)


