import unittest
from mock import MagicMock, Mock
from utils.command_context_mocker import CommandContextMocker
from utils.vm_context import VmContext
from vCenterShell.command_executer import CommandExecuterService



class TestCommandExecuterService(unittest.TestCase):
    def setUp(self):
        self.serializer = Mock()
        self.connection_retriever = Mock()
        self.connection_details = Mock()
        self.command_wrapper = Mock()
        self.connection_retriever.connection_details = Mock(return_value=self.connection_details)
        self.quali_helpers = Mock()
        CommandContextMocker.set_vm_uuid_param(VmContext.DEFAULT_NETWORK_FULL_NAME)

    def test_deploy_from_template(self):
        # arrange
        deploy_param = 'deploy_param'
        deploy_data = {'mock': Mock()}
        deploy_result = Mock()

        self.quali_helpers.get_user_param = Mock(return_value=deploy_param)
        self.serializer.decode = Mock(return_value=deploy_data)
        self.serializer.encode = Mock(return_value=True)
        self.command_wrapper.execute_command_with_connection = Mock(return_value=deploy_result)

        deploy_from_template = Mock()
        deploy_from_template.deploy_execute = Mock(return_value=True)

        command_executer_service = CommandExecuterService(self.serializer,
                                                          self.quali_helpers,
                                                          self.command_wrapper,
                                                          self.connection_retriever,
                                                          Mock(),
                                                          Mock(),
                                                          deploy_from_template,
                                                          Mock(),
                                                          Mock(),
                                                          Mock())

        # act
        command_executer_service.deploy_from_template()

        # assert
        self.assertTrue(self.quali_helpers.get_user_param.called_with('DEPLOY_DATA'))
        self.assertTrue(self.serializer.decode.called_with(deploy_param))
        self.assertTrue(self.connection_retriever.connection_details.called)
        self.assertTrue(self.command_wrapper.execute_command_with_connection.called_with(
            self.connection_details,
            deploy_from_template.execute_deploy_from_template,
            deploy_data))
        self.assertTrue(self.serializer.encode.called_with(deploy_result))

    def test_power_off(self):
        # arrange
        vcenter_name = 'name'
        resource_att = Mock()
        power_manager = Mock()
        connection_retriever = Mock()
        connection_details = Mock()
        command_wrapper = Mock()

        connection_retriever.getVCenterInventoryPathAttributeData = \
            Mock(return_value={'vCenter_resource_name': vcenter_name})
        connection_retriever.connection_details = Mock(return_value=connection_details)
        self.quali_helpers.get_resource_context_details = Mock(return_value=resource_att)
        power_manager.power_off = Mock(return_value=True)

        command_executer_service = CommandExecuterService(self.serializer,
                                                          self.quali_helpers,
                                                          self.command_wrapper,
                                                          connection_retriever,
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
        self.assertTrue(connection_retriever.getVCenterInventoryPathAttributeData.called_with(resource_att))
        self.assertTrue(command_wrapper.execute_command_with_connection.called_with(connection_details,
                                                                                    power_manager.power_off,
                                                                                    VmContext.VM_UUID))
        self.assertTrue(connection_retriever.connection_details.called_with(vcenter_name))

    def test_power_on(self):
        # arrange
        vcenter_name = 'name'
        resource_att = Mock()
        power_manager = Mock()
        connection_retriever = Mock()
        connection_details = Mock()
        command_wrapper = Mock()

        connection_retriever.getVCenterInventoryPathAttributeData = \
            Mock(return_value={'vCenter_resource_name': vcenter_name})
        connection_retriever.connection_details = Mock(return_value=connection_details)
        self.quali_helpers.get_resource_context_details = Mock(return_value=resource_att)
        power_manager.power_off = Mock(return_value=True)

        command_executer_service = CommandExecuterService(self.serializer,
                                                          self.quali_helpers,
                                                          self.command_wrapper,
                                                          connection_retriever,
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
        self.assertTrue(connection_retriever.getVCenterInventoryPathAttributeData.called_with(resource_att))
        self.assertTrue(command_wrapper.execute_command_with_connection.called_with(connection_details,
                                                                                    power_manager.power_on,
                                                                                    VmContext.VM_UUID))
        self.assertTrue(connection_retriever.connection_details.called_with(vcenter_name))

    def test_destroyVirtualMachineCommand(self):
        # arrange
        vcenter_name = 'name'
        resource_att = Mock()
        Destroyer = Mock()
        connection_retriever = Mock()
        connection_details = Mock()
        command_wrapper = Mock()

        resource_att.fullname = 'full_name'
        connection_retriever.getVCenterInventoryPathAttributeData = \
            Mock(return_value={'vCenter_resource_name': vcenter_name})
        connection_retriever.connection_details = Mock(return_value=connection_details)
        self.quali_helpers.get_resource_context_details = Mock(return_value=resource_att)
        Destroyer.power_off = Mock(return_value=True)

        command_executer_service = CommandExecuterService(self.serializer,
                                                          self.quali_helpers,
                                                          self.command_wrapper,
                                                          connection_retriever,
                                                          Destroyer,
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock(),
                                                          Mock())

        CommandContextMocker.set_vm_uuid_param(VmContext.VM_UUID)

        # act
        command_executer_service.destroy()

        # assert
        self.assertTrue(connection_retriever.getVCenterInventoryPathAttributeData.called_with(resource_att))
        self.assertTrue(command_wrapper.execute_command_with_connection.called_with(connection_details,
                                                                                    Destroyer.destroy,
                                                                                    VmContext.VM_UUID,
                                                                                    resource_att.fullname))
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