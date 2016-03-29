from unittest import TestCase
from mock import Mock
from pyVmomi import vim
from cloudshell.cp.vcenter.commands.disconnect_dvswitch import VirtualSwitchToMachineDisconnectCommand
from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from cloudshell.cp.vcenter.network.vnic.vnic_service import VNicService


class TestVirtualSwitchToMachineDisconnectCommand(TestCase):

    def test_delete_all(self):
        # arrange
        uuid = 'uuid'
        si = Mock()
        vm = Mock()

        connection_detail = Mock()
        connection_detail.host = Mock()
        connection_detail.username = Mock()
        connection_detail.password = Mock()
        connection_detail.port = Mock()

        pv_service = Mock()
        pv_service.connect = Mock(return_value=si)
        pv_service.find_by_uuid = Mock(return_value=vm)

        connector = VirtualSwitchToMachineDisconnectCommand(pv_service, Mock(), 'anetwork')
        # virtual_switch_to_machine_connector.remove_interfaces_from_vm = Mock(return_value=True)
        connector.get_network_by_name = lambda x, y: Mock()

        vcenter_data_model = VMwarevCenterResourceModel()

        # act
        res = connector.disconnect(si=si,
                                   logger=Mock(),
                                   vcenter_data_model=vcenter_data_model,
                                   vm_uuid=uuid,
                                   network_name=None,
                                   vm=None)
        # assert
        self.assertTrue(pv_service.connect.called_with(connection_detail.host,
                                                       connection_detail.username,
                                                       connection_detail.password,
                                                       connection_detail.port))
        self.assertTrue(pv_service.find_by_uuid.called_with(si, uuid))
        # self.assertTrue(virtual_switch_to_machine_connector.remove_interfaces_from_vm.called_with(vm))
        self.assertTrue(res)

    def test_delete(self):
        # arrange
        uuid = 'uuid'
        network_name = 'network_name'

        network = Mock()
        network.name = network_name
        si = Mock()
        vm = Mock()
        vm.network = [network]

        connection_detail = Mock()
        connection_detail.host = Mock()
        connection_detail.username = Mock()
        connection_detail.password = Mock()
        connection_detail.port = Mock()

        pv_service = Mock()
        pv_service.connect = Mock(return_value=si)
        pv_service.find_by_uuid = Mock(return_value=vm)

        connector = VirtualSwitchToMachineDisconnectCommand(pv_service, Mock(), 'anetwork')

        vcenter_data_model = VMwarevCenterResourceModel()

        # act
        res = connector.disconnect(si=si,
                                   logger=Mock(),
                                   vcenter_data_model=vcenter_data_model,
                                   vm_uuid= uuid,
                                   network_name=network_name)

        # assert
        self.assertTrue(pv_service.connect.called_with(connection_detail.host,
                                                       connection_detail.username,
                                                       connection_detail.password,
                                                       connection_detail.port))
        self.assertTrue(pv_service.find_by_uuid.called_with(si, uuid))
        self.assertTrue(res)

    def test_is_device_match_network_port_type(self):
        # arrange
        backing = Mock(spec=[])
        device = Mock()
        port = Mock()

        device.backing = backing
        backing.port = port
        port.portgroupKey = 'port key'

        # act
        res = VNicService.device_is_attached_to_network(device, port.portgroupKey)

        # assert
        self.assertTrue(res)

    def test_is_device_match_network_other_type(self):
        # arrange
        backing = Mock(spec=[])
        device = Mock()
        nerwork = Mock()

        device.backing = backing
        backing.network = nerwork
        nerwork.name = 'vln name or network name'

        # act
        res = VNicService.device_is_attached_to_network(device, nerwork.name)

        # assert
        self.assertTrue(res)

    def test_is_device_match_network_not_found(self):
        # arrange
        device = Mock()
        device.backing = Mock(spec=[])

        virtual_switch_to_machine_connector = VirtualSwitchToMachineDisconnectCommand(Mock(), Mock(), 'anetwork')

        # act
        # res = virtual_switch_to_machine_connector.is_device_match_network(device, 'Fake name')
        res = VNicService.device_is_attached_to_network(device, 'Fake name')

        # assert
        self.assertFalse(res)

    def test_remove_interfaces_from_vm_no_nic_found(self):
        # arrange
        vm = Mock()
        vm.config = Mock()
        vm.config.hardware()
        vm.config.hardware.device = []

        virtual_switch_to_machine_connector = VirtualSwitchToMachineDisconnectCommand(Mock(), Mock(), 'anetwork')

        # act
        res = virtual_switch_to_machine_connector.remove_interfaces_from_vm_task(vm)

        # assert
        self.assertIsNone(res)

    def test_remove_interfaces_from_vm_no_filter(self):
        # arrange
        device1 = Mock(spec=vim.vm.device.VirtualEthernetCard)
        device2 = Mock(spec=vim.vm.device.VirtualSoundCard)
        vm = Mock()
        vm.config = Mock()
        vm.config.hardware()
        vm.config.hardware.device = [device2, device1]

        virtual_switch_to_machine_connector = VirtualSwitchToMachineDisconnectCommand(Mock(), Mock(), 'anetwork')

        # act
        res = virtual_switch_to_machine_connector.remove_interfaces_from_vm_task(vm)

        # assert
        self.assertTrue(res)
        # self.assertTrue(virtual_switch_to_machine_connector.remove_devices.called)

    def test_remove_interfaces_from_vm_with_filter(self):
        # arrange
        device1 = Mock(spec=vim.vm.device.VirtualEthernetCard)
        device2 = Mock(spec=vim.vm.device.VirtualEthernetCard)
        device3 = Mock(spec=vim.vm.device.VirtualSoundCard)

        device1.name = 'this is the one'
        device2.name = 'very close'
        device3.name = 'not it'

        vm = Mock()
        vm.config = Mock()
        vm.config.hardware()
        vm.config.hardware.device = [device3, device2, device1]

        connector = VirtualSwitchToMachineDisconnectCommand(Mock(), Mock(), 'anetwork')
        #connector.remove_devices = Mock(return_value=True)

        # act
        condition = lambda device: device.name == device1.name
        res = connector.remove_interfaces_from_vm_task(vm, condition)

        # assert
        self.assertTrue(res)
        # self.assertTrue(connector.remove_devices.called)

        # def test_remove_devices(self):
        #     # arrange
        #     device_config = [Mock(spec=vim.vm.device.VirtualDeviceSpec)]
        #     task = Mock()
        #     vm = Mock()
        #     vm.ReconfigVM_Task = Mock(return_value=task)
        #
        #     virtual_switch_to_machine_connector = VirtualSwitchToMachineDisconnectCommand(Mock(), Mock(), Mock())
        #     virtual_switch_to_machine_connector.synchronous_task_waiter = Mock()
        #     virtual_switch_to_machine_connector.synchronous_task_waiter.wait_for_task = Mock(return_value=True)
        #
        #     # act
        #     res = virtual_switch_to_machine_connector.remove_devices(device_config, vm)
        #
        #     # assert
        #     self.assertTrue(res)
        #     self.assertTrue(virtual_switch_to_machine_connector.synchronous_task_waiter.wait_for_task .called_eith(task))
