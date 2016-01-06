from unittest import TestCase
from pyVmomi import vim
from mock import Mock, MagicMock

from vCenterShell.network import *
from vCenterShell.network.vnic.vnic_common import *


class TestNetwork(TestCase):
    def setUp(self):
        pass

    def test_vnic_reconfig_task(self):
        vm = Mock()
        vm.ReconfigVM_Task = lambda x: isinstance(x,  vim.vm.ConfigSpec)

        res = vm_reconfig_task(vm, [])
        self.assertTrue(res)

    def test_compose_empty(self):
        nicspec = vnic_compose_empty()
        self.assertTrue(isinstance(nicspec, vim.vm.device.VirtualDeviceSpec))
        self.assertTrue(isinstance(nicspec.device, vim.vm.device.VirtualVmxnet3))
        self.assertTrue(isinstance(nicspec.device.connectable, vim.vm.device.VirtualDevice.ConnectInfo))

    def test_device_attahed_to_network_standard(self):

        self.assertFalse(device_is_attachet_to_network(None, None))

        network_name = "TEST"
        device = Mock()
        device.backing = Mock()
        device.backing.network = Mock()
        device.backing.network.name = network_name
        self.assertTrue(device_is_attachet_to_network(device, network_name))

    def test_device_attahed_to_network_distributed(self):
        network_name = "PORT-GROUP"
        device = Mock()
        device.backing = MagicMock()
        device.backing.port = Mock()
        hasattr(device.backing, "network")
        del device.backing.network
        device.backing.port.portgroupKey = network_name
        self.assertTrue(device_is_attachet_to_network(device, network_name))


    def test_xx(self):
        vm = Mock()
        vm.ReconfigVM_Task = lambda x: isinstance(x,  vim.vm.ConfigSpec)
        nicspec = Mock()
        res = vnic_add_to_vm_task(nicspec, vm)
        self.assertIsNone(res)

        # nicspec = Mock(spec=vim.vm.device.VirtualDeviceSpec)
        # res = vnic_add_to_vm_task(nicspec, vm)
        # pass


    def test_set_connectiv(self):
        nicspec = Mock()
        nicspec.device = Mock()
        connect_status = True
        nicspec = vnic_set_connectivity_status(nicspec, connect_status)
        self.assertEquals(nicspec.device.connectable.connected, connect_status)

