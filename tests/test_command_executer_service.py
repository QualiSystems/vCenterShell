import unittest
from mock import MagicMock, Mock
from utils.command_context_mocker import CommandContextMocker
from utils.vm_context import VmContext
from vCenterShell.command_executer import CommandExecuterService



class TestCommandExecuterService(unittest.TestCase):

    def test_destroyVirtualMachineCommand(self):
        network_adapter_retriever_command = None
        destroy_virtual_machine_command = MagicMock()
        command_executer_service = CommandExecuterService(Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          destroy_virtual_machine_command,
                                                          Mock(),
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
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          deploy_from_template,
                                                          Mock(),
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
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          deploy_from_template,
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock())

        # act
        command_executer_service.deploy_from_template()

        # assert
        self.assertTrue(deploy_from_template.execute_deploy_from_template.called)

    def test_power_off(self):
        # arrange
        vcenter_name = 'name'
        helpers = Mock()
        resource_att = Mock()
        power_manager = Mock()
        logger = Mock()
        connection_retriever = Mock()
        connection_details = Mock()
        command_wrapper = Mock()
        pv_service = Mock()

        get_logger = Mock(return_value=logger)
        command_wrapper_method = Mock(return_value=command_wrapper)
        connection_retriever.getVCenterInventoryPathAttributeData = \
            Mock(return_value={'vCenter_resource_name': vcenter_name})
        connection_retriever.connection_details = Mock(return_value=connection_details)
        helpers.get_resource_context_details = Mock(return_value=resource_att)
        power_manager.power_off = Mock(return_value=True)

        command_executer_service = CommandExecuterService(helpers,
                                                          get_logger,
                                                          command_wrapper_method,
                                                          pv_service,
                                                          connection_retriever,
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          power_manager,
                                                          Mock())

        CommandContextMocker.set_vm_uuid_param(VmContext.VM_UUID)


        # act
        command_executer_service.power_off()

        # assert
        self.assertTrue(connection_retriever.getVCenterInventoryPathAttributeData.called_with(resource_att))
        self.assertTrue(get_logger.called_with('PowerOffCommand'))
        self.assertTrue(command_wrapper.execute_command_with_connection.called_with(connection_details,
                                                                                    power_manager.power_off,
                                                                                    VmContext.VM_UUID))
        self.assertTrue(command_wrapper_method.called_with(logger, pv_service))
        self.assertTrue(connection_retriever.connection_details.called_with(vcenter_name))

    def test_power_on(self):
        # arrange
        vcenter_name = 'name'
        helpers = Mock()
        resource_att = Mock()
        power_manager = Mock()
        logger = Mock()
        connection_retriever = Mock()
        connection_details = Mock()
        command_wrapper = Mock()
        pv_service = Mock()

        get_logger = Mock(return_value=logger)
        command_wrapper_method = Mock(return_value=command_wrapper)
        connection_retriever.getVCenterInventoryPathAttributeData = \
            Mock(return_value={'vCenter_resource_name': vcenter_name})
        connection_retriever.connection_details = Mock(return_value=connection_details)
        helpers.get_resource_context_details = Mock(return_value=resource_att)
        power_manager.power_off = Mock(return_value=True)

        command_executer_service = CommandExecuterService(helpers,
                                                          get_logger,
                                                          command_wrapper_method,
                                                          pv_service,
                                                          connection_retriever,
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          power_manager,
                                                          Mock())

        CommandContextMocker.set_vm_uuid_param(VmContext.VM_UUID)


        # act
        command_executer_service.power_on()

        # assert
        self.assertTrue(connection_retriever.getVCenterInventoryPathAttributeData.called_with(resource_att))
        self.assertTrue(get_logger.called_with('PowerOnCommand'))
        self.assertTrue(command_wrapper.execute_command_with_connection.called_with(connection_details,
                                                                                    power_manager.power_on,
                                                                                    VmContext.VM_UUID))
        self.assertTrue(command_wrapper_method.called_with(logger, pv_service))
        self.assertTrue(connection_retriever.connection_details.called_with(vcenter_name))

    def test_disconnect(self):
        # arrange
        virtual_switch_disconnect_command = Mock()
        virtual_switch_disconnect_command.disconnect = Mock(return_value=True)
        command_executer_service = CommandExecuterService(Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          virtual_switch_disconnect_command,
                                                          Mock(),
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
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          virtual_switch_disconnect_command,
                                                          Mock(),
                                                          Mock())

        CommandContextMocker.set_vm_uuid_param(VmContext.VM_UUID)
        CommandContextMocker.set_vm_uuid_param(VmContext.VCENTER_NAME)

        # act
        command_executer_service.disconnect_all()

        # assert
        self.assertTrue(virtual_switch_disconnect_command.disconnect_all.called)
