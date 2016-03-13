from unittest import TestCase

from mock import Mock
from pyVmomi import vim

from vCenterShell.commands.power_manager_vm import VirtualMachinePowerManagementCommand
from vCenterShell.common.logger.service import LoggingService


class TestVirtualMachinePowerManagementCommand(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def test_power_on(self):
        # arrange
        vm_uuid = 'uuid'
        si = Mock(spec=vim.ServiceInstance)
        vm = Mock(spec=vim.VirtualMachine)
        session = Mock()
        pv_service = Mock()
        pv_service.find_by_uuid = Mock(return_value=vm)

        task = Mock()

        vm.PowerOn = Mock(return_value=task)

        synchronous_task_waiter = Mock()
        synchronous_task_waiter.wait_for_task = Mock(return_value=True)

        power_manager = VirtualMachinePowerManagementCommand(pv_service, synchronous_task_waiter)

        # act
        res = power_manager.power_on(session, si, vm_uuid, None)

        # assert
        self.assertTrue(res)
        self.assertTrue(synchronous_task_waiter.wait_for_task.called_with(task))
        self.assertTrue(vm.PowerOn.called)

    def test_power_off(self):
        # arrange
        vcenter_name = 'vcenter name'
        vm_uuid = 'uuid'
        session = Mock()
        si = Mock(spec=vim.ServiceInstance)
        vm = Mock(spec=vim.VirtualMachine)
        task = Mock()
        pv_service = Mock()
        pv_service.find_by_uuid = Mock(return_value=vm)

        vm.PowerOff = Mock(return_value=task)

        synchronous_task_waiter = Mock()
        synchronous_task_waiter.wait_for_task = Mock(return_value=True)

        power_manager = VirtualMachinePowerManagementCommand(pv_service, synchronous_task_waiter)
        power_manager._connect_to_vcenter = Mock(return_value=si)
        power_manager._get_vm = Mock(return_value=vm)

        # act
        res = power_manager.power_off(session, si, vm_uuid, None)

        # assert
        self.assertTrue(res)
        self.assertTrue(power_manager._connect_to_vcenter.called_with(vcenter_name))
        self.assertTrue(power_manager._get_vm.called_with(si, vm_uuid))
        self.assertTrue(synchronous_task_waiter.wait_for_task.called_with(task))
        self.assertTrue(vm.PowerOff.called)
