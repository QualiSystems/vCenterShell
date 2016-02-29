from unittest import TestCase
from mock import Mock
from pyVmomi import vim

from vCenterShell.vm.dvswitch_connector import ConnectRequest
from vCenterShell.vm.portgroup_configurer import *


class TestDvPortGroupConfigurer(TestCase):
    def setUp(self):
        self._si = None
        self.virtual_machine_path = 'SergiiT'
        self.virtual_machine_name = 'JustTestNeedToBeRemoved'
        self.vm_uuid = "422254d5-5226-946e-26fb-60c21898b731"

        self.vcenter_name = "QualiSB"
        self.port_group_path = 'QualiSB'
        self.dv_switch_path = 'QualiSB'
        self.network_path = 'QualiSB'

        self.dv_switch_name = 'dvSwitch-SergiiT'
        self.dv_port_group_name = 'aa-dvPortGroup3B'

        self.network = Mock()
        self.network.key = "network-key"
        self.network.config.distributedVirtualSwitch.uuid = "422254d5-5226-946e-26fb-60c21898b73f"
        self.py_vmomi_service = Mock()

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

        mapping = {'vnic 1': Mock(spec=vim.Network)}
        self.vnic_service = Mock()
        self.vnic_to_network_mapper = Mock()
        self.vnic_to_network_mapper.map_request_to_vnics = Mock(return_value=mapping)
        self.vnics = {'vnic 1': self.vnic}

        self.vnic_service.map_vnics = Mock(return_value=self.vnics)
        self.configurer = VirtualMachinePortGroupConfigurer(self.py_vmomi_service,
                                                            self.synchronous_task_waiter,
                                                            self.vnic_to_network_mapper,
                                                            self.vnic_service)

    def test_erase_network_by_mapping(self):
        mapping = [self.vnic, self.network, False, None]
        res = self.configurer.erase_network_by_mapping(self.vm, [mapping])
        self.assertIsNone(res)

    def test_disconnect_all_networks(self):
        mapping = self.configurer.disconnect_all_networks(self.vm, Mock(spec=vim.Network))
        self.assertFalse(mapping[0].connect)

    def test_disconnect_network(self):
        mapping = self.configurer.disconnect_network(self.vm, self.network,  Mock(spec=vim.Network))
        self.assertFalse(mapping[0].connect)

    def test_connect_vnic_to_networks(self):
        req  = ConnectRequest('vnic 1', Mock(spec=vim.Network))
        mapping = [ConnectRequest('vnic 1', Mock(spec=vim.Network))]
        res = self.configurer.connect_vnic_to_networks(self.vm, mapping, Mock(spec=vim.Network), [])
        self.assertIsNotNone(res[0].vnic)
