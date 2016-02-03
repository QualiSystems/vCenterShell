from unittest import TestCase

from mock import patch, Mock

from vCenterShell.commands.command_orchestrator import CommandOrchestrator

class MockResourceParser(object):
    @staticmethod
    def convert_to_resource_model(dummy, resource):
        return resource


class Test_command_orchestrator(TestCase):
    @patch('common.model_factory.ResourceModelParser.convert_to_resource_model',
           MockResourceParser.convert_to_resource_model)
    def setUp(self):
        self.resource = Mock()
        self.context = Mock()
        session = Mock()
        self.connection_details = Mock()
        self.context.resource = self.resource
        self.command_orchestrator = CommandOrchestrator(self.context)
        self.command_orchestrator.command_wrapper.execute_command_with_connection = Mock(return_value=True)
        self.command_orchestrator.cs_helper = Mock()
        self.command_orchestrator.cs_helper.get_session = Mock(return_value=session)
        self.command_orchestrator.cs_helper.get_connection_details = Mock(return_value=self.connection_details)
        self.command_orchestrator.vc_data_model.default_dvswitch_path = 'path'
        self.command_orchestrator.vc_data_model.default_dvswitch_name = 'dv_name'
        self.command_orchestrator.vc_data_model.default_port_group_path = 'port path'
        self.command_orchestrator.vc_data_model.default_network = 'default network'

    def test_connect(self):
        # act
        res = self.command_orchestrator.connect(self.context, 'uuid', 'vlan id', 'vlan type')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)
        self.assertTrue(res)

    def test_disconnect_all(self):
        # act
        self.command_orchestrator.disconnect_all(self.context, 'uuid')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_disconnect(self):
        # act
        self.command_orchestrator.disconnect(self.context, 'uuid', 'network')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_destroy_vm(self):
        # act
        self.command_orchestrator.destroy_vm(self.context, 'uuid', 'full_name')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_deploy_from_template(self):
        # act
        self.command_orchestrator.deploy_from_template(self.context, '{"name": "name"}')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_power_off(self):
        # act
        self.command_orchestrator.power_off(self.context, 'uuid', 'full_name')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_power_on(self):
        # act
        self.command_orchestrator.power_on(self.context, 'uuid', 'full_name')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)

    def test_refresh_ip(self):
        # act
        self.command_orchestrator.refresh_ip(self.context, 'uuid', 'full_name')
        # assert
        self.assertTrue(self.command_orchestrator.command_wrapper.execute_command_with_connection.called)