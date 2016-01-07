
class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self,
                 serializer,
                 qualipy_helpers,
                 logger_retriever,
                 pv_service,
                 command_wrapper,
                 connection_retriever,
                 destroy_virtual_machine_command,
                 deploy_from_template_command,
                 virtual_switch_connect_command,
                 virtual_switch_disconnect_command,
                 vm_power_management_command):
        self.serializer = serializer
        self.qualipy_helpers = qualipy_helpers
        self.get_logger = logger_retriever
        self.pv_service = pv_service
        self.command_wrappper = command_wrapper
        self.connection_retriever = connection_retriever
        self.destroyVirtualMachineCommand = destroy_virtual_machine_command
        self.deployFromTemplateCommand = deploy_from_template_command
        self.virtual_switch_connect_command = virtual_switch_connect_command
        self.virtual_switch_disconnect_command = virtual_switch_disconnect_command
        self.vm_power_management_command = vm_power_management_command

    def destroy(self):
        self.disconnect_all()
        self.destroyVirtualMachineCommand.execute()

    def connect(self):
        vlan_id = self.qualipy_helpers.get_user_param('VLAN_ID')
        vlan_spec_type = self.qualipy_helpers.get_user_param('VLAN_SPEC_TYPE')
        self.virtual_switch_connect_command.connect_vm_to_vlan(vlan_id, vlan_spec_type)

    def disconnect_all(self):
        # todo: the vcenter param should be getting inside the command from resource
        vcener_name = self.qualipy_helpers.get_user_param('VCENTER_NAME')
        virtual_machine_id = self.qualipy_helpers.get_user_param('VM_UUID')
        self.virtual_switch_disconnect_command.disconnect_all(vcener_name, virtual_machine_id)

    def disconnect(self):
        # todo: the vcenter param should be getting inside the command from resource
        vcener_name = self.qualipy_helpers.get_user_param('VCENTER_NAME')
        virtual_machine_id = self.qualipy_helpers.get_user_param('VM_UUID')
        network_name = self.qualipy_helpers.get_user_param('NETWORK_NAME')
        self.virtual_switch_disconnect_command.disconnect(vcener_name, virtual_machine_id, network_name)

    def deploy_from_template(self):
        # get command parameters from the environment
        deployment_params = self.qualipy_helpers.get_user_param('DEPLOY_DATA')
        data = self.serializer.decode(deployment_params)

        # prepare for execute command
        command_wrapper = self.init_command_wrapper('DeployFromTemplate')
        connection_details = self.get_vcenter_connection_details()

        # execute command
        result = command_wrapper.execute_command_with_connection(
                                                            connection_details,
                                                            self.deployFromTemplateCommand.execute_deploy_from_template,
                                                            data)
        print self.serializer.encode(result)

    def power_off(self):
        # get command parameters from the environment
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')

        # prepare for execute command
        command_wrapper = self.init_command_wrapper('PowerOffCommand')
        connection_details = self.get_vcenter_connection_details()

        # execute command
        command_wrapper.execute_command_with_connection(connection_details,
                                                        self.vm_power_management_command.power_off,
                                                        vm_uuid)

    def power_on(self):
        # get command parameters from the environment
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')

        # prepare for execute command
        command_wrapper = self.init_command_wrapper('PowerOnCommand')
        connection_details = self.get_vcenter_connection_details()

        # execute command
        command_wrapper.execute_command_with_connection(connection_details,
                                                        self.vm_power_management_command.power_on,
                                                        vm_uuid)

    def init_command_wrapper(self, command_name):
        logger = self.get_logger(command_name)
        command_wrapper = self.command_wrappper(logger, self.pv_service)
        return command_wrapper

    def get_vcenter_connection_details(self):
        """
        connects to the specified vCenter
        :rtype vim.ServiceInstance: si
        """
        # gets the name of the vcenter to connect
        resource_att = self.qualipy_helpers.get_resource_context_details()
        inventory_path_data = self.connection_retriever.getVCenterInventoryPathAttributeData(resource_att)
        vcenter_resource_name = inventory_path_data['vCenter_resource_name']
        connection_details = self.connection_retriever.connection_details(vcenter_resource_name)
        return connection_details
