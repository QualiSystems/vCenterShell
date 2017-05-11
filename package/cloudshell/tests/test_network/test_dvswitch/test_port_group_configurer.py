from unittest import TestCase

from cloudshell.cp.vcenter.network.dvswitch.name_generator import DvPortGroupNameGenerator
from cloudshell.cp.vcenter.vm.portgroup_configurer import VirtualMachinePortGroupConfigurer
from mock import Mock, MagicMock
from pyVmomi import vim

from cloudshell.cp.vcenter.vm.dvswitch_connector import ConnectRequest


class TestDvPortGroupConfigurer(TestCase):
    def setUp(self):
        self._si = None
        self.virtual_machine_path = 'SergiiT'
        self.virtual_machine_name = 'JustTestNeedToBeRemoved'
        self.vm_uuid = "422254d5-5226-946e-26fb-60c21898b731"

        self.vcenter_name = "QualiSB"
        self.dv_switch_path = 'QualiSB'
        self.network_path = 'QualiSB'

        self.dv_switch_name = 'dvSwitch-SergiiT'
        self.dv_port_group_name = 'aa-dvPortGroup3B'

        self.network = Mock()
        self.network.key = "network-key"
        self.network.name = "QS_123"
        self.network.config.distributedVirtualSwitch.uuid = "422254d5-5226-946e-26fb-60c21898b73f"
        self.py_vmomi_service = Mock()

        self.network2 = Mock()
        self.network2.key = "network2-key"
        self.network2.name = "QS_network2"
        self.network3 = Mock()
        self.network3.key = "network3-key"
        self.network3.name = "QS_network3"

        self.vm = Mock()
        self.vm.config.hardware = Mock()
        self.vnic = Mock(spec=vim.vm.device.VirtualEthernetCard)
        self.vnic.macAddress = True
        self.vnic.deviceInfo = Mock()
        self.vm.config.hardware.device = [self.vnic]
        self.py_vmomi_service.find_by_uuid = lambda a, b, c: self.vm
        self.py_vmomi_service.find_network_by_name = Mock(return_value=self.network)

        self.synchronous_task_waiter = Mock()
        self.synchronous_task_waiter.wait_for_task = Mock(return_value="TASK OK")
        self.si = Mock()

        mapping = {'vnic 1': (Mock(spec=vim.Network), None)}
        self.vnic_service = Mock()
        self.vnic_to_network_mapper = Mock()
        self.vnic_to_network_mapper.map_request_to_vnics = Mock(return_value=mapping)
        self.vnics = {'vnic 1': self.vnic}

        self.port_group_name_generator = DvPortGroupNameGenerator()

        self.vnic_service.map_vnics = Mock(return_value=self.vnics)
        self.configurer = VirtualMachinePortGroupConfigurer(self.py_vmomi_service,
                                                            self.synchronous_task_waiter,
                                                            self.vnic_to_network_mapper,
                                                            self.vnic_service,
                                                            self.port_group_name_generator)

    def test_get_networks_on_vnics(self):
        res = self.configurer.get_networks_on_vnics(self.vm, [self.vnic], logger=Mock())
        self.assertIsNotNone(res)

    def test_erase_network_by_mapping(self):
        res = self.configurer.erase_network_by_mapping([self.network], [], logger=Mock())
        self.assertIsNone(res)

    def test_disconnect_all_networks(self):
        mapping = self.configurer.disconnect_all_networks(self.vm, Mock(spec=vim.Network), [], logger=Mock())
        self.assertFalse(mapping[0].connect)

    def test_disconnect_network(self):
        mapping = self.configurer.disconnect_network(self.vm, self.network, Mock(spec=vim.Network), '', logger=Mock())
        self.assertFalse(mapping[0].connect)

    def test_connect_vnic_to_networks(self):
        mapping = [ConnectRequest('vnic 1', (Mock(spec=vim.Network), None))]
        res = self.configurer.connect_vnic_to_networks(self.vm, mapping, Mock(spec=vim.Network), [], logger=Mock())
        self.assertIsNotNone(res[0].vnic)

    def test_disconnect_network_that_two_vms_have(self):
        def side_effect(*args, **keys):
            del self.network.name

        self.network.vm = None
        self.port_group_name_generator.is_generated_name = MagicMock(return_value=True)
        self.configurer.destroy_port_group_task = MagicMock(side_effect=side_effect)
        self.configurer.erase_network_by_mapping([self.network, self.network], [], logger=Mock())

    def test_disconnect_vm_with_three_networks(self):
        def side_effect(*args, **keys):
            del args[0].name

        self.network.vm = None
        self.network2.vm = None
        self.network3.vm = None
        self.port_group_name_generator.is_generated_name = MagicMock(return_value=True)
        self.configurer.destroy_port_group_task = MagicMock(side_effect=side_effect)
        self.configurer.erase_network_by_mapping([self.network, self.network2, self.network3], [], logger=Mock())

        # Assert
        self.assertFalse(hasattr(self.network, 'name'))
        self.assertFalse(hasattr(self.network2, 'name'))
        self.assertFalse(hasattr(self.network3, 'name'))
