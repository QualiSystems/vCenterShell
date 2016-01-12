from vCenterShell.vm.dvswitch_connector import VmNetworkMapping


class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self,
                 serializer,
                 qualipy_helpers,
                 command_wrapper,
                 connection_retriever,
                 vcenter_resource_model,
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
        self.vcenter_resource_model = vcenter_resource_model
        self.destroyVirtualMachineCommand = destroy_virtual_machine_command
        self.deployFromTemplateCommand = deploy_from_template_command
        self.virtual_switch_connect_command = virtual_switch_connect_command
        self.virtual_switch_disconnect_command = virtual_switch_disconnect_command
        self.vm_power_management_command = vm_power_management_command
        self.refresh_ip_command = refresh_ip_command

    def connect(self):
        # get command parameters from the environment
        uuid = self.qualipy_helpers.get_user_param('UUID')
        vlan_id = self.qualipy_helpers.get_user_param('VLAN_ID')
        vlan_spec_type = self.qualipy_helpers.get_user_param('VLAN_SPEC_TYPE')
        vnic_name = self.qualipy_helpers.get_user_param('VNIC_NAME')
        dv_port_name = self.qualipy_helpers.get_user_param('DV_PORT_NAME')

        # load default params
        dv_switch_path = self.vcenter_resource_model.default_dvswitch_path
        dv_switch_name = self.vcenter_resource_model.default_dvswitch_name
        port_group_path = self.vcenter_resource_model.default_port_group_path

        vnic_to_network = self.create_vnic_to_network_map(dv_port_name,
                                                          dv_switch_name,
                                                          dv_switch_path,
                                                          port_group_path,
                                                          vlan_id,
                                                          vlan_spec_type,
                                                          vnic_name)

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(
            connection_details,
            self.virtual_switch_connect_command.connect_to_networks,
            uuid,
            [vnic_to_network])

    def disconnect_all(self):
        vcener_name = self.qualipy_helpers.get_user_param('VCENTER_NAME')
        virtual_machine_id = self.qualipy_helpers.get_user_param('VM_UUID')
        default_network_name = self.qualipy_helpers.get_user_param('DEFAULT_NETWORK_FULL_NAME')
        self.virtual_switch_disconnect_command.disconnect_all(vcener_name, virtual_machine_id, default_network_name)

    def disconnect(self):
        vcener_name = self.qualipy_helpers.get_user_param('VCENTER_NAME')
        virtual_machine_id = self.qualipy_helpers.get_user_param('VM_UUID')
        network_name = self.qualipy_helpers.get_user_param('NETWORK_NAME')
        default_network_name = self.qualipy_helpers.get_user_param('DEFAULT_NETWORK_FULL_NAME')
        self.virtual_switch_disconnect_command.disconnect(vcener_name, virtual_machine_id, network_name,
                                                          default_network_name)

    def destroy(self):
        # get command parameters from the environment
        uuid = self.qualipy_helpers.get_user_param('uuid')
        resource = self.qualipy_helpers.get_resource_context_details()

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(
            connection_details,
            self.destroyVirtualMachineCommand.destroy,
            uuid,
            resource.fullname)

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
