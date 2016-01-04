from unittest import TestCase

from mock import Mock
from pyVmomi import vim

from pycommon.logging_service import LoggingService
from vCenterShell.commands.VirtualMachinePowerManagementCommand import VirtualMachinePowerManagementCommand


class TestVirtualMachinePowerManagementCommand(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def test_get_vm_found(self):
        # arrange
        si = Mock(spec=vim.ServiceInstance)
        vm_uuid = 'uuid'
        vm = Mock()

        pv_service = Mock()
        pv_service.find_by_uuid = Mock(return_value=vm)

        power_manager = VirtualMachinePowerManagementCommand(pv_service, Mock(), Mock(), Mock())

        # act
        res = power_manager._get_vm(si, vm_uuid)

        # assert
        self.assertTrue(pv_service.find_by_uuid.called_with(si, vm_uuid))
        self.assertEqual(res, vm)

    def test_get_vm_not_found(self):
        # arrange
        si = Mock(spec=vim.ServiceInstance)
        vm_uuid = 'uuid'

        pv_service = Mock()
        pv_service.find_by_uuid = Mock(return_value=None)

        power_manager = VirtualMachinePowerManagementCommand(pv_service, Mock(), Mock(), Mock())

        # assert
        self.assertRaises(Exception, power_manager._get_vm, si, vm_uuid)
        self.assertTrue(pv_service.find_by_uuid.called_with(si, vm_uuid))

    def test_connect_to_vcenter(self):
        # arrange
        si = Mock(spec=vim.ServiceInstance)
        vcenter_name = 'vcenter name'
        connection_detail = Mock()
        connection_retriever = Mock()
        resource_att = Mock()
        qualipy_helpers = Mock()
        pv_service = Mock()

        inventory_path_data = {'vCenter_resource_name': Mock()}
        qualipy_helpers.get_resource_context_details = Mock(return_value=resource_att)
        connection_retriever.getVCenterInventoryPathAttributeData = \
            Mock(return_value=inventory_path_data)

        connection_detail.host = 'host'
        connection_detail.username = 'username'
        connection_detail.password = 'password'
        connection_detail.port = 'port'

        connection_retriever.connection_details = Mock(return_value=connection_detail)

        pv_service.connect = Mock(return_value=si)

        power_manager = VirtualMachinePowerManagementCommand(pv_service, connection_retriever, Mock(), qualipy_helpers)

        # act
        res = power_manager._connect_to_vcenter()

        # assert
        self.assertEqual(si, res)
        self.assertTrue(connection_retriever.connection_details.called_with(vcenter_name))
        self.assertTrue( pv_service.connect.called_with(connection_detail.host,
                                                        connection_detail.username,
                                                        connection_detail.password,
                                                        connection_detail.port))

    def test_power_on(self):
        # arrange
        vcenter_name = 'vcenter name'
        vm_uuid = 'uuid'
        si = Mock(spec=vim.ServiceInstance)
        vm = Mock(spec=vim.VirtualMachine)
        task = Mock()

        vm.PowerOn = Mock(return_value=task)

        synchronous_task_waiter = Mock()
        synchronous_task_waiter.wait_for_task = Mock(return_value=True)

        power_manager = VirtualMachinePowerManagementCommand(Mock(), Mock(), synchronous_task_waiter, Mock())
        power_manager._connect_to_vcenter = Mock(return_value=si)
        power_manager._get_vm = Mock(return_value=vm)

        # act
        res = power_manager.power_on(vm_uuid)

        # assert
        self.assertTrue(res)
        self.assertTrue(power_manager._connect_to_vcenter.called_with(vcenter_name))
        self.assertTrue(power_manager._get_vm.called_with(si, vm_uuid))
        self.assertTrue(synchronous_task_waiter.wait_for_task.called_with(task))
        self.assertTrue(vm.PowerOn.called)

    def test_power_off(self):
        # arrange
        vcenter_name = 'vcenter name'
        vm_uuid = 'uuid'
        si = Mock(spec=vim.ServiceInstance)
        vm = Mock(spec=vim.VirtualMachine)
        task = Mock()

        vm.PowerOff = Mock(return_value=task)

        synchronous_task_waiter = Mock()
        synchronous_task_waiter.wait_for_task = Mock(return_value=True)

        power_manager = VirtualMachinePowerManagementCommand(Mock(), Mock(), synchronous_task_waiter, Mock())
        power_manager._connect_to_vcenter = Mock(return_value=si)
        power_manager._get_vm = Mock(return_value=vm)

        # act
        res = power_manager.power_off(vm_uuid)

        # assert
        self.assertTrue(res)
        self.assertTrue(power_manager._connect_to_vcenter.called_with(vcenter_name))
        self.assertTrue(power_manager._get_vm.called_with(si, vm_uuid))
        self.assertTrue(synchronous_task_waiter.wait_for_task.called_with(task))
        self.assertTrue(vm.PowerOff.called)
