from unittest import TestCase

from cloudshell.api.cloudshell_api import ResourceInfo
from cloudshell.cp.vcenter.commands.command_orchestrator import CommandOrchestrator
from mock import Mock, create_autospec


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

    def test_destroy_vm(self):
        # act
        self.command_orchestrator.destroy_vm(self.context, self.ports)
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
