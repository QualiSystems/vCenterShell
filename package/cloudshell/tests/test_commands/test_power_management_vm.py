from unittest import TestCase
from mock import Mock
from pyVmomi import vim
from cloudshell.cp.vcenter.commands.power_manager_vm import VirtualMachinePowerManagementCommand


class TestVirtualMachinePowerManagementCommand(TestCase):
    def test_power_off_already(self):
        vm_uuid = 'uuid'
        si = Mock(spec=vim.ServiceInstance)
        vm = Mock(spec=vim.VirtualMachine)
        vm.summary = Mock()
        vm.summary.runtime = Mock()
        vm.summary.runtime.powerState = 'poweredOff'
        session = Mock()
        pv_service = Mock()
        pv_service.find_by_uuid = Mock(return_value=vm)

        power_manager = VirtualMachinePowerManagementCommand(pv_service, Mock())

        # act
        res = power_manager.power_off(si=si,
                                      logger=Mock(),
                                      session=session,
                                      vcenter_data_model=Mock(),
                                      vm_uuid=vm_uuid,
                                      resource_fullname=None)

        # assert
        self.assertTrue(res, 'already powered off')
        self.assertFalse(vm.PowerOn.called)

    def test_power_on_already(self):
        vm_uuid = 'uuid'
        si = Mock(spec=vim.ServiceInstance)
        vm = Mock(spec=vim.VirtualMachine)
        vm.summary = Mock()
        vm.summary.runtime = Mock()
        vm.summary.runtime.powerState = 'poweredOn'
        session = Mock()
        pv_service = Mock()
        pv_service.find_by_uuid = Mock(return_value=vm)

        power_manager = VirtualMachinePowerManagementCommand(pv_service, Mock())

        # act
        res = power_manager.power_on(si=si,
                                     logger=Mock(),
                                     session=session,
                                     vm_uuid=vm_uuid,
                                     resource_fullname=None)

        # assert
        self.assertTrue(res, 'already powered on')
        self.assertFalse(vm.PowerOn.called)

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
        res = power_manager.power_on(si=si,
                                     logger=Mock(),
                                     session=session,
                                     vm_uuid=vm_uuid,
                                     resource_fullname=None)

        # assert
        self.assertTrue(res)
        self.assertTrue(synchronous_task_waiter.wait_for_task.called_with(task))
        self.assertTrue(vm.PowerOn.called)

    def test_power_off_soft(self):
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

        vcenter = Mock()
        vcenter.shutdown_method = 'soft'
        # act
        res = power_manager.power_off(si=si,
                                      logger=Mock(),
                                      session=session,
                                      vcenter_data_model=vcenter,
                                      vm_uuid=vm_uuid,
                                      resource_fullname=None)

        # assert
        self.assertTrue(res)
        self.assertTrue(vm.ShutdownGuest.called)
        self.assertTrue(power_manager._connect_to_vcenter.called_with(vcenter_name))
        self.assertTrue(power_manager._get_vm.called_with(si, vm_uuid))
        self.assertTrue(synchronous_task_waiter.wait_for_task.called_with(task))

    def test_power_off_hard(self):
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

        vcenter = Mock()
        vcenter.shutdown_method = 'hard'
        # act
        res = power_manager.power_off(si=si,
                                      logger=Mock(),
                                      session=session,
                                      vcenter_data_model=vcenter,
                                      vm_uuid=vm_uuid,
                                      resource_fullname=None)

        # assert
        self.assertTrue(res)
        self.assertTrue(vm.PowerOff.called)
        self.assertTrue(power_manager._connect_to_vcenter.called_with(vcenter_name))
        self.assertTrue(power_manager._get_vm.called_with(si, vm_uuid))
        self.assertTrue(synchronous_task_waiter.wait_for_task.called_with(task))
