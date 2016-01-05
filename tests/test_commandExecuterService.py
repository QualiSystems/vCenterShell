import unittest

from mock import MagicMock, Mock

from common.command_context_mocker import *
from common.vm_context import *
from vCenterShell.command_executer import CommandExecuterService


class TestCommandExecuterService(unittest.TestCase):

    def test_destroyVirtualMachineCommand(self):
        network_adapter_retriever_command = None
        destroy_virtual_machine_command = MagicMock()
        command_executer_service = CommandExecuterService(None,
                                                          network_adapter_retriever_command,
                                                          destroy_virtual_machine_command,
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock())

        CommandContextMocker.set_vm_uuid_param(VmContext.VM_UUID)
        CommandContextMocker.set_vm_uuid_param(VmContext.VCENTER_NAME)

        command_executer_service.destroy()

        destroy_virtual_machine_command.execute.assert_called_with()

    def test_deploy_from_template_deploy(self):
        # arrange
        deploy_from_template = Mock()
        deploy_from_template.execute = Mock(return_value=True)
        command_executer_service = CommandExecuterService(Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          deploy_from_template,
                                                          Mock(),
                                                          Mock(),
                                                          Mock())

        # act
        command_executer_service.deploy()

        # assert
        self.assertTrue(deploy_from_template.execute.called)

    def test_deploy_from_template(self):
        # arrange
        deploy_from_template = Mock()
        deploy_from_template.deploy_execute = Mock(return_value=True)
        command_executer_service = CommandExecuterService(Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          deploy_from_template,
                                                          Mock(),
                                                          Mock(),
                                                          Mock())

        # act
        command_executer_service.deploy_from_template()

        # assert
        self.assertTrue(deploy_from_template.execute_deploy_from_template.called)

    def test_power_off(self):
        # arrange
        power_manager = Mock()
        power_manager.power_off = Mock(return_value=True)
        command_executer_service = CommandExecuterService(Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          power_manager)

        CommandContextMocker.set_vm_uuid_param(VmContext.VM_UUID)


        # act
        command_executer_service.power_off()

        # assert
        self.assertTrue(power_manager.power_off.called)

    def test_power_on(self):
        # arrange
        power_manager = Mock()
        power_manager.power_on = Mock(return_value=True)
        command_executer_service = CommandExecuterService(Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          power_manager)

        CommandContextMocker.set_vm_uuid_param(VmContext.VM_UUID)
        # act
        command_executer_service.power_on()

        # assert
        self.assertTrue(power_manager.power_on.called)

    def test_disconnect(self):
        # arrange
        virtual_switch_disconnect_command = Mock()
        virtual_switch_disconnect_command.disconnect = Mock(return_value=True)
        command_executer_service = CommandExecuterService(Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          virtual_switch_disconnect_command,
                                                          Mock())


        CommandContextMocker.set_vm_uuid_param(VmContext.VM_UUID)
        CommandContextMocker.set_vm_uuid_param(VmContext.VCENTER_NAME)
        CommandContextMocker.set_vm_uuid_param(VmContext.NETWORK_NAME)

        # act
        command_executer_service.disconnect()

        # assert
        self.assertTrue(virtual_switch_disconnect_command.disconnect.called)

    def test_disconnect_all(self):
        # arrange
        virtual_switch_disconnect_command = Mock()
        virtual_switch_disconnect_command.disconnect_all = Mock(return_value=True)
        command_executer_service = CommandExecuterService(Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          virtual_switch_disconnect_command,
                                                          Mock())

        CommandContextMocker.set_vm_uuid_param(VmContext.VM_UUID)
        CommandContextMocker.set_vm_uuid_param(VmContext.VCENTER_NAME)

        # act
        command_executer_service.disconnect_all()

        # assert
        self.assertTrue(virtual_switch_disconnect_command.disconnect_all.called)

