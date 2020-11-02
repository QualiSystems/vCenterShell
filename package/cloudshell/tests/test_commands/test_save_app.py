from unittest import TestCase
from mock import Mock, PropertyMock
from uuid import uuid4 as guid

from cloudshell.cp.vcenter.commands.save_sandbox import SaveAppCommand
from cloudshell.cp.core.models import SaveApp, SaveAppParams

from cloudshell.cp.vcenter.common.vcenter.folder_manager import FolderManager
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.vcenter.models.QualiDriverModels import CancellationContext


class MockResourceParser(object):
    @staticmethod
    def convert_to_resource_model(dummy, callable):
        return callable()


class TestSaveAppCommand(TestCase):
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
        self.save_command = SaveAppCommand(pyvmomi_service=self.pyvmomi_service,
                                           task_waiter=Mock(),
                                           deployer=self.deployer,
                                           resource_model_parser=MockResourceParser(),
                                           snapshot_saver=Mock(),
                                           folder_manager=self.folder_manager,
                                           cancellation_service=self.cancellation_service,
                                           port_group_configurer=Mock())

    def test_save_runs_successfully(self):
        # receive a save request with 2 actions, return a save response with 2 results.
        # baseline test
        save_action1 = self._create_arbitrary_save_app_action()
        save_action2 = self._create_arbitrary_save_app_action()

        # path to save apps folder and saved sandbox folder uses default datacenter and vm location
        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        vcenter_data_model.holding_network = 'DEFAULT NETWORK'

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action1, save_action2],
                                            cancellation_context=self.cancellation_context)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].actionId == save_action1.actionId)
        self.assertTrue(result[0].success)

        self.assertTrue(result[1].type == 'SaveApp')
        self.assertTrue(result[1].actionId == save_action2.actionId)
        self.assertTrue(result[1].success)

    def test_exception_thrown_if_command_cancelled_before_anything_runs(self):
        save_action1 = self._create_arbitrary_save_app_action()
        save_action2 = self._create_arbitrary_save_app_action()

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'

        cancellation_context = Mock()
        cancellation_context.is_cancelled = True

        with self.assertRaises(Exception) as context:
            self.save_command.save_app(si=Mock(),
                                       logger=Mock(),
                                       vcenter_data_model=vcenter_data_model,
                                       reservation_id='abc',
                                       save_app_actions=[save_action1, save_action2],
                                       cancellation_context=cancellation_context)
            self.assertIn('Save sandbox was cancelled', str(context.exception))

    def test_destroy_on_vms_and_folders_if_command_cancelled_during_deploy(self):
        save_action1 = self._create_arbitrary_save_app_action()
        save_action2 = self._create_arbitrary_save_app_action()

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'

        return_values = [False, True]

        cancellation_service = Mock()
        cancellation_service.check_if_cancelled = Mock(side_effect=return_values)

        self.save_command = SaveAppCommand(pyvmomi_service=self.pyvmomi_service,
                                           task_waiter=Mock(),
                                           deployer=self.deployer,
                                           resource_model_parser=MockResourceParser(),
                                           snapshot_saver=Mock(),
                                           folder_manager=self.folder_manager,
                                           cancellation_service=cancellation_service,
                                           port_group_configurer=Mock())

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action1, save_action2],
                                            cancellation_context=self.cancellation_context)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].actionId == save_action1.actionId)
        self.assertTrue(result[0].errorMessage == 'Save app action {0} was rolled back'.format(save_action1.actionId))
        self.assertTrue(not result[0].success)

        self.assertTrue(result[1].type == 'SaveApp')
        self.assertTrue(result[1].actionId == save_action2.actionId)
        self.assertTrue(result[0].errorMessage == 'Save app action {0} was rolled back'.format(save_action2.actionId))
        self.assertTrue(not result[1].success)

    def test_nonempty_saved_sandbox_storage_replaces_default_storage(self):
        # receive a save request with 2 actions, return a save response with 2 results.
        # baseline test
        save_action1 = self._create_arbitrary_save_app_action()

        # path to save apps folder and saved sandbox folder uses default datacenter and vm location
        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        vcenter_data_model.saved_sandbox_storage = 'sandbox_storage'
        vcenter_data_model.vm_storage = 'default_storage'

        self.save_command.save_app(si=Mock(),
                                   logger=Mock(),
                                   vcenter_data_model=vcenter_data_model,
                                   reservation_id='abc',
                                   save_app_actions=[save_action1],
                                   cancellation_context=self.cancellation_context)

        # Assert
        deploy_method_mock = self.save_command.deployer.deploy_clone_from_vm
        args = deploy_method_mock.call_args_list[0][0]  # [0] = get first call of method [0] = get *args
        data_holder = next(a for a in args if isinstance(a, DeployFromTemplateDetails))

        self.assertTrue(data_holder.template_resource_model.vm_storage == vcenter_data_model.saved_sandbox_storage)

    def test_empty_saved_sandbox_storage_does_not_replace_default_storage(self):
        # receive a save request with 2 actions, return a save response with 2 results.
        # baseline test
        save_action1 = self._create_arbitrary_save_app_action()

        # path to save apps folder and saved sandbox folder uses default datacenter and vm location
        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        vcenter_data_model.saved_sandbox_storage = ''
        vcenter_data_model.vm_storage = 'default_storage'

        self.save_command.save_app(si=Mock(),
                                   logger=Mock(),
                                   vcenter_data_model=vcenter_data_model,
                                   reservation_id='abc',
                                   save_app_actions=[save_action1],
                                   cancellation_context=self.cancellation_context)

        # Assert
        deploy_method_mock = self.save_command.deployer.deploy_clone_from_vm
        args = deploy_method_mock.call_args_list[0][0]  # [0] = get first call of method [0] = get *args
        data_holder = next(a for a in args if isinstance(a, DeployFromTemplateDetails))

        self.assertTrue(data_holder.template_resource_model.vm_storage == vcenter_data_model.vm_storage)

    def test_behavior_during_save_configured_as_power_off(self):
        # if user configured the save app action behavior during clone as power off
        # the vm, assuming it was powered on when save started
        # will power off, clone will occur, and then will power on

        save_action = self._create_arbitrary_save_app_action()
        save_action.actionParams.deploymentPathAttributes['Behavior during save'] = 'Power Off'

        vm = Mock()
        vm.summary.runtime.powerState = 'poweredOn'
        vm.name = 'some string'
        self.save_command.pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        vcenter_data_model.holding_network = 'DEFAULT NETWORK'

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action],
                                            cancellation_context=self.cancellation_context)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].success)

        self.assertTrue(vm.PowerOff.called)
        self.assertTrue(vm.PowerOff.called)

    def test_behavior_during_save_configured_as_power_off_on_vcenter_model_empty_on_deployment_option(self):
        # if behavior during save is empty on deployment, default to vcenter model

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        vcenter_data_model.holding_network = 'DEFAULT NETWORK'

        save_action = self._create_arbitrary_save_app_action()
        save_action.actionParams.deploymentPathAttributes['Behavior during save'] = ''
        vcenter_data_model.behavior_during_save = 'Power Off'

        vm = Mock()
        vm.summary.runtime.powerState = 'poweredOn'
        vm.name = 'some string'
        self.save_command.pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action],
                                            cancellation_context=self.cancellation_context)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].success)

        self.assertTrue(vm.PowerOff.called)
        self.assertTrue(vm.PowerOff.called)

    def test_create_saved_apps_folder_if_not_found_in_vcenter(self):
        # vcenter folder under the vm location, will be created when it doesnt exist.
        # a typical scheme would be QualiSB\Qualifolder\Saved Sandboxes
        # where QualiSB is datacenter, QualiFolder is vm location,
        # and Saved Sandboxes is the folder under which apps will be saved
        # (under Saved Sandboxes there is a folder for each sandbox)

        save_action = self._create_arbitrary_save_app_action()

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        vcenter_data_model.holding_network = 'DEFAULT NETWORK'

        vm_location_folder = Mock()

        self.save_command.pyvmomi_service.get_folder = Mock(side_effect=[vm_location_folder, None, None,
                                                                         vm_location_folder, vm_location_folder,
                                                                         vm_location_folder])

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action],
                                            cancellation_context=self.cancellation_context)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].success)

        # Saved Sandboxes folder was created
        vm_location_folder.CreateFolder.assert_called_with('Saved Sandboxes')

    def test_create_saved_sandbox_folder_if_not_found_in_vcenter(self):
        # show the sandbox folder under saved apps folder is created when doesnt exist
        save_action = self._create_arbitrary_save_app_action()

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        vcenter_data_model.holding_network = 'DEFAULT NETWORK'

        saved_apps_folder = Mock()

        def cant_find_saved_apps_folder(si, path):
            if path == vcenter_data_model.default_datacenter + '/' \
                    + vcenter_data_model.vm_location + '/' \
                    + 'Saved Sandboxes' '/' \
                    + save_action.actionParams.savedSandboxId:
                return None
            return saved_apps_folder

        self.save_command.pyvmomi_service.get_folder = Mock(side_effect=cant_find_saved_apps_folder)

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action],
                                            cancellation_context=self.cancellation_context)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].success)

        # saved sandbox folder was created
        saved_apps_folder.CreateFolder.assert_called_with(save_action.actionParams.savedSandboxId)

    def test_save_fails_when_actions_empty(self):
        # exception will be thrown if save actions list is empty in request

        with self.assertRaises(Exception) as context:
            self._save_app_without_actions()
        self.assertIn('Failed to save app, missing data in request.', str(context.exception))

    def test_error_thrown_during_save(self):
        # if error is thrown during save, SaveAppResult will still be returned,
        # with success=False,
        # and error message=exception message

        save_action = self._create_arbitrary_save_app_action()

        self.save_command.deployer = Mock()
        error_message = 'Save app action  was rolled back'
        self.save_command.deployer.deploy_clone_from_vm = Mock(side_effect=Exception(error_message))

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action],
                                            cancellation_context=self.cancellation_context)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(not result[0].success)
        self.assertTrue(result[0].errorMessage == error_message)

    def test_save_fails_due_to_unsupported_save_type(self):
        # if cloud provider sends an invalid save action with unsupported save type
        # an exception will be thrown

        save_action = self._create_arbitrary_save_app_action()
        save_action.actionParams.saveDeploymentModel = 'mass quantum cloning'

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action],
                                            cancellation_context=None)

        # Assert
        self.assertTrue(not result[0].success)
        self.assertTrue(result[0].errorMessage == 'Unsupported save type {0}'
                        .format(save_action.actionParams.saveDeploymentModel))

    def _save_app_without_actions(self):
        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'
        self.save_command.save_app(si=Mock(),
                                   logger=Mock(),
                                   vcenter_data_model=vcenter_data_model,
                                   reservation_id='abc',
                                   save_app_actions=[],
                                   cancellation_context=None)

    def _create_arbitrary_save_app_action(self):
        save_action = SaveApp()
        actionParams = SaveAppParams()
        actionParams.saveDeploymentModel = 'VCenter Deploy VM From Linked Clone'
        actionParams.savedSandboxId = str(guid())
        actionParams.sourceVmUuid = str(guid())
        actionParams.deploymentPathAttributes = dict()

        save_action.actionParams = actionParams
        return save_action
