from unittest import TestCase
from mock import Mock, MagicMock, create_autospec

from pyVmomi import vim
from common.vcenter.vmomi_service import *
from vCenterShell.network.vnic.vnic_service import VNicService


class TestNetwork(TestCase):
    def setUp(self):
        pass

    def test_vnic_reconfig_task(self):
        vm = Mock()
        vm.ReconfigVM_Task = lambda x: isinstance(x,  vim.vm.ConfigSpec)

        api_wrapper = pyVmomiService(Mock, Mock())
        res = api_wrapper.vm_reconfig_task(vm, [])
        self.assertTrue(res)

    def test_compose_empty(self):
        nicspec = VNicService.vnic_compose_empty()
        self.assertTrue(isinstance(nicspec, vim.vm.device.VirtualDeviceSpec))
        self.assertTrue(isinstance(nicspec.device, vim.vm.device.VirtualVmxnet3))
        self.assertTrue(isinstance(nicspec.device.connectable, vim.vm.device.VirtualDevice.ConnectInfo))

    def test_device_attahed_to_network_standard(self):

        self.assertFalse(VNicService.device_is_attached_to_network(None, None))

        network_name = "TEST"
        device = Mock()
        device.backing = Mock()
        device.backing.network = Mock()
        device.backing.network.name = network_name
        self.assertTrue(VNicService.device_is_attached_to_network(device, network_name))

        network = Mock(spec=vim.Network)
        network.name = "xnet"
        nicspec = Mock()

        nicspec.device = device
        res = VNicService.vnic_attach_to_network_standard(nicspec, network)
        self.assertEquals(res.device.backing.network.name, "xnet")

    def test_device_attahed_to_network_distributed(self):
        network_name = "PORT-GROUP"
        device = Mock()
        device.backing = MagicMock()
        device.backing.port = Mock()
        hasattr(device.backing, "network")
        del device.backing.network
        device.backing.port.portgroupKey = network_name
        self.assertTrue(VNicService.device_is_attached_to_network(device, network_name))

        port_group = Mock(spec=vim.dvs.DistributedVirtualPortgroup)
        port_group.key = "group_net"
        port_group.config.distributedVirtualSwitch.uuid = "6686"
        nicspec = Mock()

        nicspec.device = device
        res = VNicService.vnic_attach_to_network_distributed(nicspec, port_group)
        self.assertEquals(res.device.backing.port.portgroupKey, "group_net")


    def test_xx(self):
        vm = Mock()
        vm.ReconfigVM_Task = lambda x: isinstance(x,  vim.vm.ConfigSpec)
        nicspec = Mock()
        res = VNicService.vnic_add_to_vm_task(nicspec, vm)
        self.assertIsNone(res)

        # nicspec = Mock(spec=vim.vm.device.VirtualDeviceSpec)
        # res = vnic_add_to_vm_task(nicspec, vm)
        # pass


    def test_set_connectiv(self):
        nicspec = Mock()
        nicspec.device = Mock()
        connect_status = True
        nicspec = VNicService.vnic_set_connectivity_status(nicspec, connect_status)
        self.assertEquals(nicspec.device.connectable.connected, connect_status)


    def test_vnic_is_attachet_to_network(self):
        nicspec = Mock()
        nicspec.device = Mock()
        res = VNicService.vnic_is_attachet_to_network(nicspec, Mock())
        self.assertFalse(res)

    def test_vnic_remove_from_vm_list(self):
        #arrange
        vm = create_autospec(spec=vim.vm)
        vm.config = Mock()
        vm.config.hardware = Mock()
        vm.config.hardware.device = [create_autospec(spec=vim.vm.device.VirtualEthernetCard)]

        #act
        device_change = VNicService.vnic_remove_from_vm_list(vm)

        #assert
        self.assertTrue(len(device_change) == 1)

    def test_get_device_spec(self):
        #arrange
        vnic = Mock()
        VNicService.create_vnic_spec = Mock()
        VNicService.set_vnic_connectivity_status = Mock()

        #act
        VNicService.get_device_spec(vnic, True)

        #assert
        self.assertTrue(VNicService.create_vnic_spec.called)
        self.assertTrue(VNicService.set_vnic_connectivity_status.called)

    def test_vnic_add_new_to_vm_task(self):
        #arrange

        vm = create_autospec(spec=vim.vm)
        VNicService.vnic_new_attached_to_network = Mock()
        #VNicService.vnic_add_to_vm_task = Mock()

        #act
        VNicService.vnic_add_new_to_vm_task(vm)

        #assert
        self.assertTrue(VNicService.vnic_new_attached_to_network.called)
        # self.assertTrue(VNicService.vnic_add_to_vm_task.called)

    def test_vnic_attached_to_network_1(self):
        #arrange
        network = create_autospec(spec=vim.dvs.DistributedVirtualPortgroup)
        nicspec = create_autospec(spec=vim.vm.device.VirtualDeviceSpec)
        VNicService.vnic_attach_to_network_distributed = Mock()

        #act
        VNicService.vnic_attached_to_network(nicspec, network)

        #assert
        self.assertTrue(VNicService.vnic_attach_to_network_distributed.called)

    def test_vnic_attached_to_network_2(self):
        #arrange
        network = create_autospec(spec=vim.Network)
        nicspec = create_autospec(spec=vim.vm.device.VirtualDeviceSpec)
        VNicService.vnic_attach_to_network_standard = Mock()

        #act
        VNicService.vnic_attached_to_network(nicspec, network)

        #assert
        self.assertTrue(VNicService.vnic_attach_to_network_standard.called)