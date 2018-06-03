from unittest import TestCase
from mock import Mock
from uuid import uuid4 as guid

from cloudshell.cp.vcenter.commands.save_app import SaveAppCommand
from cloudshell.cp.core.models import SaveApp, SaveAppParams


class MockResourceParser(object):
    @staticmethod
    def convert_to_resource_model(dummy, callable):
        return callable()


class TestSaveAppCommand(TestCase):
    def setUp(self):
        self.pyvmomi_service = Mock()
        vm = Mock()
        vm.name = 'some string'
        self.pyvmomi_service.get_vm_by_uuid = Mock(return_value=vm)
        self.save_command = SaveAppCommand(pyvmomi_service=self.pyvmomi_service,
                                           task_waiter=Mock(),
                                           deployer=Mock(),
                                           resource_model_parser=MockResourceParser(),
                                           snapshot_saver=Mock())
        clone_result = Mock()
        clone_result.vmName = 'whatever'
        self.save_command.deployer.deploy_clone_from_vm = Mock(return_value=clone_result)


    def test_save_runs_successfully(self):
        # receive a save request with 2 actions, return a save response with 2 results.
        # baseline test
        save_action1 = self._create_arbitrary_save_app_action()
        save_action2 = self._create_arbitrary_save_app_action()

        # path to save apps folder and saved sandbox folder uses default datacenter and vm location
        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action1, save_action2],
                                            cancellation_context=None)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].actionId == save_action1.actionId)
        self.assertTrue(result[0].success)

        self.assertTrue(result[1].type == 'SaveApp')
        self.assertTrue(result[1].actionId == save_action2.actionId)
        self.assertTrue(result[1].success)

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
        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action],
                                            cancellation_context=None)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].success)

        self.assertTrue(vm.PowerOff.called)
        self.assertTrue(vm.PowerOff.called)

    def test_create_saved_apps_folder_if_not_found_in_vcenter(self):
        # vcenter folder under the vm location, will be created when it doesnt exist.
        # a typical scheme would be QualiSB\Qualifolder\SavedApps
        # where QualiSB is datacenter, QualiFolder is vm location,
        # and SavedApps is the folder under which apps will be saved
        # (under SavedApps there is a folder for each sandbox)

        save_action = self._create_arbitrary_save_app_action()

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'

        vm_location_folder = Mock()

        def cant_find_saved_apps_folder(si, path):
            if path == vcenter_data_model.default_datacenter + '/' \
                    + vcenter_data_model.vm_location + '/'\
                    + 'SavedApps':
                return None
            return vm_location_folder

        self.save_command.pyvmomi_service.get_folder = Mock(side_effect=cant_find_saved_apps_folder)

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action],
                                            cancellation_context=None)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].success)

        # SavedApps folder was created
        vm_location_folder.CreateFolder.assert_called_with('SavedApps')

    def test_create_saved_sandbox_folder_if_not_found_in_vcenter(self):
        # show the sandbox folder under saved apps folder is created when doesnt exist
        save_action = self._create_arbitrary_save_app_action()

        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'QualiSB Cluster'
        vcenter_data_model.vm_location = 'QualiFolder'

        saved_apps_folder = Mock()

        def cant_find_saved_apps_folder(si, path):
            if path == vcenter_data_model.default_datacenter + '/' \
                    + vcenter_data_model.vm_location + '/'\
                    + 'SavedApps' '/'\
                    + save_action.actionParams.savedSandboxId:
                return None
            return saved_apps_folder

        self.save_command.pyvmomi_service.get_folder = Mock(side_effect=cant_find_saved_apps_folder)

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            vcenter_data_model=vcenter_data_model,
                                            reservation_id='abc',
                                            save_app_actions=[save_action],
                                            cancellation_context=None)

        # Assert
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(result[0].success)

        # saved sandbox folder was created
        saved_apps_folder.CreateFolder.assert_called_with(save_action.actionParams.savedSandboxId)

    def test_save_fails_when_actions_empty(self):
        # exception will be thrown if save actions list is empty in request

        with self.assertRaises(Exception) as context:
            self._save_app_without_actions()
        self.assertIn('Failed to save app, missing data in request.', context.exception.message)

    def test_error_thrown_during_save(self):
        # if error is thrown during save, SaveAppResult will still be returned,
        # with success=False,
        # and error message=exception message

        save_action = self._create_arbitrary_save_app_action()

        self.save_command.deployer = Mock()
        error_message = 'Clone VM failed!'
        self.save_command.deployer.deploy_clone_from_vm = Mock(side_effect=Exception(error_message))

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
        self.assertTrue(result[0].type == 'SaveApp')
        self.assertTrue(not result[0].success)
        self.assertTrue(result[0].errorMessage==error_message)

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
