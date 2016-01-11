from unittest import TestCase

from mock import Mock

from pyVmomi import vim
from vCenterShell.vm.portgroup_configurer import *


class TestDvPortGroupConfigurer(TestCase):
    def setUp(self):
        self._si = None
        self.virtual_machine_path = 'SergiiT'
        self.virtual_machine_name = 'JustTestNeedToBeRemoved'
        self.vm_uuid = "422254d5-5226-946e-26fb-60c21898b731"

        self.vcenter_name    = "QualiSB"
        self.port_group_path = 'QualiSB'
        self.dv_switch_path  = 'QualiSB'
        self.network_path    = 'QualiSB'

        self.dv_switch_name = 'dvSwitch-SergiiT'
        self.dv_port_group_name = 'aa-dvPortGroup3B'

        self.network = Mock()
        self.network.key = "network-key"
        self.network.config.distributedVirtualSwitch.uuid = "422254d5-5226-946e-26fb-60c21898b73f"
        self.py_vmomi_service = Mock()

        self.vm = Mock()
        self.vm.config.hardware = Mock()
        self.vnic = Mock(spec=vim.vm.device.VirtualEthernetCard)
        self.vnic.deviceInfo = Mock()
        self.vm.config.hardware.device = [self.vnic]


        self.nspec =  vnic_compose_empty(self.vnic)
        # self.vm.config.hardware.device.deviceInfo = Mock()
        # self.vm.config.hardware.device.deviceInfo.label = ""

        self.py_vmomi_service.find_by_uuid = lambda a, b, c: self.vm
        self.py_vmomi_service.find_network_by_name = Mock(return_value=self.network)


        self.synchronous_task_waiter = Mock()
        self.synchronous_task_waiter.wait_for_task = Mock(return_value="TASK OK")
        self.si = Mock()

        self.configurer = VirtualMachinePortGroupConfigurer(self.py_vmomi_service, self.synchronous_task_waiter)
        self.configurer.get_device_spec = Mock(return_value=self.nspec)

    def test_configure_port_group_on_vm(self):
        res = self.configurer.configure_port_group_on_vm(self.si,
                                              self.virtual_machine_path,
                                              self.vm_uuid,
                                              self.port_group_path,
                                              self.dv_port_group_name)

        self.assertEquals(res, "TASK OK")

    def test_map_vnc(self):
        res = self.configurer.map_vnics(self.vm)
        self.assertEquals(len(res), 1)

    def test_get_device_spec(self):
        res = self.configurer.get_device_spec(self.vnic, False)
        self.assertIsInstance(res, vim.vm.device.VirtualDeviceSpec)

    # def test_create_vnic_spec(self):
    #     nic_spec = Mock()
    #     self.configurer.set_vnic_connectivity_status(nic_spec, True)
    #     self.assertEquals(nic_spec.device.connectable.startConnected, True)


    def test_erase_network_by_mapping(self):
        mapping = [self.vnic, self.network, False, None]
        res = self.configurer.erase_network_by_mapping(self.vm, [mapping])
        self.assertIsNone(res)

    def test_update_vnic_by_mapping(self):
        mapping = [self.vnic, self.network, False, None]
        res = self.configurer.update_vnic_by_mapping(self.vm, [mapping])
        self.assertEquals(res, "TASK OK")

    def test_disconnect_all_networks(self):
        res = self.configurer.disconnect_all_networks(self.vm)
        self.assertIsNone(res)

    def test_disconnect_network(self):
        res = self.configurer.disconnect_network(self.vm, self.network)
        self.assertIsNone(res)

    def test_connect_first_available_vnic(self):
        res = self.configurer.connect_first_available_vnic(self.vm, self.network)
        self.assertEquals(res, "TASK OK")

    def test_connect_vinc_port_group(self):

        res = self.configurer.connect_vinc_port_group(self.vm, "name", self.network)
        self.assertIsNone(res)