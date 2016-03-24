from unittest import TestCase
from cloudshell.api.cloudshell_api import ResourceInfo
from mock import Mock, patch, MagicMock, create_autospec
from vcentershell_driver.driver import VCenterShellDriver



class TestCommandOrchestrator(TestCase):
    def setUp(self):
        self.driver = VCenterShellDriver()
        self.resource = create_autospec(ResourceInfo)
        self.resource.ResourceModelName = 'VMware vCenter'
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
                                            'Default Datacenter': 'QualiSB'}
        self.context = Mock()
        self.context.resource = self.resource
        self.driver.command_orchestrator = MagicMock()
        self.cancellation_context = Mock()
        self.ports = Mock()

    def test_init(self):
        self.driver.initialize()

    def test_connect_bulk(self):
        self.setUp()
        requset = Mock()

        res = self.driver.ApplyConnectivityChanges(self.context, requset)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.connect_bulk.called_with(self.context, requset, []))

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

    def test_deploy_from_image(self):
        self.setUp()
        deploy_data = Mock()

        res = self.driver.deploy_from_image(self.context, deploy_data)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator.deploy_from_image.called_with(self.context,
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

        res = self.driver.remote_refresh_ip(self.context, self.cancellation_context, self.ports)

        self.assertIsNotNone(res)
        self.assertTrue(self.driver.command_orchestrator._refresh_ip.called_with(self.context, self.cancellation_context, self.ports))
