from unittest import TestCase

from mock import Mock, patch, MagicMock

from vcentershell_driver.driver import VCenterShellDriver

class MockResourceParser(object):
    @staticmethod
    def convert_to_resource_model(dummy, resource):
        return resource


class Test_command_orchestrator(TestCase):
    def setUp(self):
        self.driver = VCenterShellDriver()
        self.resource = Mock()
        self.context = Mock()
        self.context.resource = self.resource
        self.driver.command_orchestrator = MagicMock()
        self.ports = Mock()

    @patch('common.model_factory.ResourceModelParser.convert_to_resource_model',
           MockResourceParser.convert_to_resource_model)
    def test_init(self):
        self.driver.initialize(self.context)

    def test_connect_bulk(self):
        self.setUp()
        requset = Mock()

        res = self.driver.Connect(self.context, requset)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.connect_bulk.called_with(self.context, requset))

    # def test_connect(self):
    #     self.setUp()
    #     vm_uuid = Mock()
    #     vlan_id = Mock()
    #     vlan_spec_type = Mock()
    #
    #     res = self.driver.connect(self.context, vm_uuid, vlan_id, vlan_spec_type)
    #
    #     self.assertIsNotNone(res)
    #     self.assertTrue(self.driver.command_orchestrator.connect.called_with(self.context, vm_uuid,
    #                                                                               vlan_id, vlan_spec_type))

    def test_disconnect_all(self):
        self.setUp()

        res = self.driver.disconnect_all(self.context, self.ports)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.disconnect_all.called_with(self.context, self.ports))

    def test_disconnect(self):
        self.setUp()
        network_name = Mock()

        res = self.driver.disconnect(self.context, self.ports, network_name)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.disconnect.called_with(self.context, self.ports, network_name))

    def test_destroy_vm(self):
        self.setUp()

        res = self.driver.remote_destroy_vm(self.context, self.ports)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.destroy_vm.called_with(self.context, self.ports))

    def test_deploy_from_template(self):
        self.setUp()
        deploy_data = Mock()

        res = self.driver.deploy_from_template(self.context, deploy_data)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.deploy_from_template.called_with(self.context,
                                                                                          deploy_data))

    def test_power_off(self):
        self.setUp()

        res = self.driver.PowerOff(self.context, self.ports)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.power_off.called_with(self.context, self.ports))

    def test_power_on(self):
        self.setUp()

        res = self.driver.PowerOn(self.context, self.ports)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.power_on.called_with(self.context, self.ports))

    def test_power_cycle(self):
        self.setUp()

        res = self.driver.PowerCycle(self.context, self.ports, 10)

        self.assertIsNotNone(res)

    def test_refresh_ip(self):
        self.setUp()

        res = self.driver.remote_refresh_ip(self.context, self.ports)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.refresh_ip.called_with(self.context,self.ports))