from unittest import TestCase
from mock import Mock, PropertyMock
from uuid import uuid4 as guid

from cloudshell.cp.vcenter.commands.delete_saved_sandbox import DeleteSavedSandboxCommand
from cloudshell.cp.vcenter.commands.save_sandbox import SaveAppCommand
from cloudshell.cp.core.models import SaveApp, SaveAppParams, DeleteSavedApp, DeleteSavedAppParams, Artifact

from cloudshell.cp.vcenter.common.vcenter.folder_manager import FolderManager
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.vcenter.models.QualiDriverModels import CancellationContext


class MockResourceParser(object):
    @staticmethod
    def convert_to_resource_model(dummy, callable):
        return callable()


class TestDeleteSavedSandboxCommand(TestCase):
    def setUp(self):
        self.pyvmomi_service = Mock()
        self.cancellation_context = Mock()
        self.cancellation_context.is_cancelled = False
        vm = Mock()
        vm.name = 'some string'
        task_waiter = Mock()
        self.folder_manager = FolderManager(self.pyvmomi_service, task_waiter)
        self.pyvmomi_service.get_vm_by_uuid = Mock(return_value=vm)
        self.cancellation_service = Mock()
        self.cancellation_service.check_if_cancelled = Mock(return_value=False)
        clone_result = Mock(vmName='whatever')
        self.deployer = Mock()
        self.deployer.deploy_clone_from_vm = Mock(return_value=clone_result)
        self.delete_command = DeleteSavedSandboxCommand(pyvmomi_service=self.pyvmomi_service,
                                                        task_waiter=Mock(),
                                                        deployer=self.deployer,
                                                        resource_model_parser=MockResourceParser(),
                                                        snapshot_saver=Mock(),
                                                        folder_manager=self.folder_manager,
                                                        cancellation_service=self.cancellation_service,
                                                        port_group_configurer=Mock())

    def test_delete_sandbox_runs_successfully(self):
        # receive a save request with 2 actions, return a save response with 2 results.
        # baseline test
        delete_action1 = self._create_arbitrary_delete_saved_app_action()
        delete_action2 = self._create_arbitrary_delete_saved_app_action()

        # path to save apps folder and saved sandbox folder uses default datacenter and vm location
        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        vcenter_data_model.holding_network = 'DEFAULT NETWORK'

        result = self.delete_command.delete_sandbox(si=Mock(),
                                                    logger=Mock(),
                                                    vcenter_data_model=vcenter_data_model,
                                                    delete_sandbox_actions=[delete_action1, delete_action2],
                                                    cancellation_context=self.cancellation_context)

        # Assert
        self.assertTrue(result[0].type == 'DeleteSavedApp')
        self.assertTrue(result[0].actionId == delete_action1.actionId)
        self.assertTrue(result[0].success)

        self.assertTrue(result[1].type == 'DeleteSavedApp')
        self.assertTrue(result[1].actionId == delete_action2.actionId)
        self.assertTrue(result[1].success)

    def test_delete_saved_sandbox_fails_when_actions_empty(self):
        # exception will be thrown if save actions list is empty in request

        with self.assertRaises(Exception) as context:
            self._delete_saved_sandbox_without_actions()
        self.assertIn('Failed to delete saved sandbox, missing data in request.', str(context.exception))

    def test_delete_saved_sandbox_fails_due_to_unsupported_save_type(self):
        # if cloud provider sends an invalid delete save action with unsupported save type
        # an exception will be thrown

        delete_action = self._create_arbitrary_delete_saved_app_action()
        delete_action.actionParams.saveDeploymentModel = 'mass quantum cloning'

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        result = self.delete_command.delete_sandbox(si=Mock(),
                                                    logger=Mock(),
                                                    vcenter_data_model=vcenter_data_model,
                                                    delete_sandbox_actions=[delete_action],
                                                    cancellation_context=self.cancellation_context)
        # Assert
        self.assertTrue(not result[0].success)
        self.assertTrue(result[0].errorMessage == 'Unsupported save deployment models: {0}'
                        .format(delete_action.actionParams.saveDeploymentModel))

    def _delete_saved_sandbox_without_actions(self):
        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        self.delete_command.delete_sandbox(si=Mock(),
                                           logger=Mock(),
                                           vcenter_data_model=vcenter_data_model,
                                           delete_sandbox_actions=[],
                                           cancellation_context=self.cancellation_context)

    def _create_arbitrary_delete_saved_app_action(self):
        save_action = DeleteSavedApp()
        actionParams = DeleteSavedAppParams()
        actionParams.artifacts = [Artifact(artifactRef=guid(), artifactName=guid())]
        actionParams.saveDeploymentModel = 'VCenter Deploy VM From Linked Clone'
        actionParams.savedSandboxId = str(guid())
        actionParams.sourceVmUuid = str(guid())
        actionParams.deploymentPathAttributes = dict()

        save_action.actionParams = actionParams
        return save_action
