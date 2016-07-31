from unittest import TestCase

import jsonpickle
from cloudshell.api.cloudshell_api import ResourceInfo
from cloudshell.cp.vcenter.commands.command_orchestrator import CommandOrchestrator
from cloudshell.shell.core.driver_context import ResourceRemoteCommandContext, ResourceContextDetails, AppContext
from mock import Mock, create_autospec, patch

RESTORE_SNAPSHOT = 'cloudshell.cp.vcenter.commands.command_orchestrator.CommandOrchestrator.restore_snapshot'
SAVE_SNAPSHOT = 'cloudshell.cp.vcenter.commands.command_orchestrator.CommandOrchestrator.save_snapshot'


class TestCommandOrchestrator(TestCase):
    def setUp(self):
        self.resource = create_autospec(ResourceInfo)
        self.resource.ResourceModelName = 'VMwarev Center'
        self.resource.ResourceAttributes = {'User': 'user',
                                            'Password': '123',
                                            'Default dvSwitch': 'switch1',
                                            'Holding Network': 'anetwork',
                                            'Default Port Group Location': 'Quali',
                                            'VM Cluster': 'Quali',
                                            'VM Location': 'Quali',
                                            'VM Resource Pool': 'Quali',
                                            'VM Storage': 'Quali',
                                            'Shutdown Method': 'hard',
                                            'OVF Tool Path': 'C\\program files\ovf',
                                            'Execution Server Selector': '',
                                            'Reserved Networks': 'vlan65',
                                            'Default Datacenter': 'QualiSB'
                                            }
        self.context = Mock()
        session = Mock()
        remote_resource = Mock()
        remote_resource.fullname = 'this is full name of the remote resource'
        remote_resource.uuid = 'this is full uuis of the remote resource'
        self.connection_details = Mock()
        self.context.resource = self.resource
        self.context.remote_endpoints = [self.resource]
        self.command_orchestrator = CommandOrchestrator()
        self.command_orchestrator.command_wrapper.execute_command_with_connection = Mock(return_value=True)
        self.command_orchestrator.cs_helper = Mock()
        self.command_orchestrator.cs_helper.get_session = Mock(return_value=session)
        self.command_orchestrator.cs_helper.get_connection_details = Mock(return_value=self.connection_details)
        self.ports = [Mock()]
        self.command_orchestrator._parse_remote_model = Mock(return_value=remote_resource)

    def test_disconnect_all(self):
        # act
        self.command_orchestrator.disconnect_all(self.context, self.ports)
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_disconnect(self):
        # act
        self.command_orchestrator.disconnect(self.context, self.ports, 'network')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_destroy_vm_only(self):
        # act
        self.command_orchestrator.destroy_vm_only(self.context, self.ports)
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_deploy_from_template(self):
        # act
        self.command_orchestrator.deploy_from_template(self.context,
                                                       '{"name": "name", "template_resource_model": {"vcenter_template": ""}}')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_deploy_vm_from_vm(self):
        # act
        self.command_orchestrator.deploy_clone_from_vm(self.context,
                                                       '{"name": "name", "template_resource_model": {"vcenter_vm": ""}}')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_deploy_from_snapshot(self):
        # act
        self.command_orchestrator.deploy_from_linked_clone(self.context,
                                                           '{"name": "name", "template_resource_model": {"vcenter_vm": "name", "vcenter_vm_snapshot": "snap"}}')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_deploy_from_image(self):
        # act
        self.command_orchestrator.deploy_from_image(self.context, '{"name": "name"}')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_power_off(self):
        # act
        self.command_orchestrator.power_off(self.context, self.ports)
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_power_on(self):
        # act
        self.command_orchestrator.power_on(self.context, self.ports)
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_power_cycle(self):
        # act
        self.command_orchestrator.power_cycle(self.context, self.ports, 0.0001)
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_refresh_ip(self):
        # act
        cancellation_context = object()
        self.command_orchestrator.refresh_ip(self.context, cancellation_context=cancellation_context, ports=self.ports)
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_get_uuid(self):
        self.command_orchestrator.get_vm_uuid_by_name(self.context, 'Name')
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_save_snapshot(self):
        self.command_orchestrator.save_snapshot(self.context, 'new_snapshot')
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_restore_snapshot(self):
        self.command_orchestrator.restore_snapshot(self.context, 'new_snapshot')
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_get_snapshots(self):
        self.command_orchestrator.get_snapshots(self.context)
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_orchestration_save(self):
        # Arrange
        with patch(SAVE_SNAPSHOT) as save_snapshot_mock:
            save_snapshot_mock.return_value = '"new_snapshot"'

            remote_command_context = create_autospec(ResourceRemoteCommandContext)
            remote_command_context.resource = create_autospec(ResourceContextDetails)
            remote_command_context.resource.fullname = 'vcenter'
            endpoint = create_autospec(ResourceContextDetails)
            endpoint.fullname = 'vm_111'
            endpoint.app_context = create_autospec(AppContext)
            endpoint.app_context.deployed_app_json = '{"vmdetails": {"uid": "vm_uuid1"}}'
            remote_command_context.remote_endpoints = [endpoint]

            # Act
            saved_result = CommandOrchestrator().orchestration_save(context=remote_command_context,
                                                                    mode='shallow',
                                                                    custom_params=None)

            # Assert
            save_snapshot_mock.assert_called_once()
            saved_result_dict = jsonpickle.decode(saved_result)
            self.assertEqual(saved_result_dict['saved_artifacts_info']['saved_artifact']['artifact_type'],
                             'vcenter_snapshot')
            self.assertEqual(saved_result_dict['saved_artifacts_info']['saved_artifact']['identifier'], 'new_snapshot')
            self.assertEqual(saved_result_dict['saved_artifacts_info']['resource_name'], 'vcenter')
            self.assertIsNotNone(saved_result_dict['saved_artifacts_info']['created_date'])

    def test_orchestration_restore(self):
        # Arrange
        with patch(RESTORE_SNAPSHOT) as mock_restore_snapshot:
            # Act
            self.command_orchestrator.orchestration_restore(self.context, '''{
      "saved_artifacts_info": {
        "resource_name": "ex cillum sed laboris",
        "created_date": "4313-10-12T18:03:15.053Z",
        "restore_rules": {
          "requires_same_resource": false
        },
        "saved_artifact": {
          "artifact_type": "veniam in qui",
          "identifier": "deserunt1"
        }
      }
    }''')
            # Assert
            mock_restore_snapshot.assert_called_once_with(context=self.context, snapshot_name='deserunt1')
