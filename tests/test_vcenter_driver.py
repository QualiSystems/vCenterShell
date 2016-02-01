from unittest import TestCase

from mock import patch, Mock

from vcentershell_driver.driver import VCenterShellDriver


class MockResourceParser(object):
    @staticmethod
    def convert_to_resource_model(dummy, resource):
        return resource


class TestVCenterDriver(TestCase):
    @patch('common.model_factory.ResourceModelParser.convert_to_resource_model',
           MockResourceParser.convert_to_resource_model)
    def setUp(self):
        self.driver = VCenterShellDriver()
        self.resource = Mock()
        self.context = Mock()
        session = Mock()
        self.connection_details = Mock()
        self.context.resource = self.resource
        self.driver.initialize(self.context)
        self.driver.command_wrapper.execute_command_with_connection = Mock(return_value=True)
        self.driver.cs_helper = Mock()
        self.driver.cs_helper.get_session = Mock(return_value=session)
        self.driver.cs_helper.get_connection_details = Mock(return_value=self.connection_details)
        self.driver.vc_data_model.default_dvswitch_path = 'path'
        self.driver.vc_data_model.default_dvswitch_name = 'dv_name'
        self.driver.vc_data_model.default_port_group_path = 'port path'
        self.driver.vc_data_model.default_network = 'default network'

    def test_connect(self):
        # act
        res = self.driver.connect(self.context, 'uuid', 'vlan id', 'vlan type')
        # assert
        self.assertTrue(self.driver.command_wrapper.execute_command_with_connection.called)
        self.assertTrue(res)

    def test_disconnect_all(self):
        # act
        self.driver.disconnect_all(self.context, 'uuid')
        # assert
        self.assertTrue(self.driver.command_wrapper.execute_command_with_connection.called)

    def test_disconnect(self):
        # act
        self.driver.disconnect(self.context, 'uuid', 'network')
        # assert
        self.assertTrue(self.driver.command_wrapper.execute_command_with_connection.called)

    def test_destroy_vm(self):
        # act
        self.driver.destroy_vm(self.context, 'uuid', 'full_name')
        # assert
        self.assertTrue(self.driver.command_wrapper.execute_command_with_connection.called)

    def test_deploy_from_template(self):
        # act
        self.driver.deploy_from_template(self.context, '{"name": "name"}')
        # assert
        self.assertTrue(self.driver.command_wrapper.execute_command_with_connection.called)

    def test_power_off(self):
        # act
        self.driver.power_off(self.context, 'uuid', 'full_name')
        # assert
        self.assertTrue(self.driver.command_wrapper.execute_command_with_connection.called)

    def test_power_on(self):
        # act
        self.driver.power_on(self.context, 'uuid', 'full_name')
        # assert
        self.assertTrue(self.driver.command_wrapper.execute_command_with_connection.called)

    def test_refresh_ip(self):
        # act
        self.driver.refresh_ip(self.context, 'uuid', 'full_name')
        # assert
        self.assertTrue(self.driver.command_wrapper.execute_command_with_connection.called)