class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self,
                 serializer,
                 qualipy_helpers,
                 command_wrapper,
                 connection_retriever,
                 destroy_virtual_machine_command,
                 deploy_from_template_command,
                 virtual_switch_connect_command,
                 virtual_switch_disconnect_command,
                 vm_power_management_command,
                 refresh_ip_command):
        self.serializer = serializer
        self.qualipy_helpers = qualipy_helpers
        self.command_wrapper = command_wrapper
        self.connection_retriever = connection_retriever
        self.destroyVirtualMachineCommand = destroy_virtual_machine_command
        self.deployFromTemplateCommand = deploy_from_template_command
        self.virtual_switch_connect_command = virtual_switch_connect_command
        self.virtual_switch_disconnect_command = virtual_switch_disconnect_command
        self.vm_power_management_command = vm_power_management_command
        self.refresh_ip_command = refresh_ip_command

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
        connection_details = self.connection_retriever.connection_details()

        # execute command
        result = self.command_wrapper.execute_command_with_connection(
            connection_details,
            self.deployFromTemplateCommand.execute_deploy_from_template,
            data)
        print self.serializer.encode(result)

    def power_off(self):
        # get command parameters from the environment
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(connection_details,
                                                             self.vm_power_management_command.power_off,
                                                             vm_uuid)

    def power_on(self):
        # get command parameters from the environment
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(connection_details,
                                                             self.vm_power_management_command.power_on,
                                                             vm_uuid)

    def refresh_ip(self):
        # get command parameters from the environment
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')
        resource_name = self.qualipy_helpers.get_user_param('RESOURCE_NAME')

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.execute_command_with_connection(connection_details,
                                             self.refresh_ip_command.refresh_ip,
                                             vm_uuid,
                                             resource_name)
