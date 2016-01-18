from models.DeployDataHolder import DeployDataHolder
from vCenterShell.vm.dvswitch_connector import VmNetworkMapping


class CommandExecuterService(object):
    """ main class that publishes all available commands """

    COMMAND_RESULT_PREFIX = "command_json_result="
    COMMAND_RESULT_POSTFIX = "=command_json_result_end"

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
        uuid = self.qualipy_helpers.get_user_param('VM_UUID')
        vlan_id = self.qualipy_helpers.get_user_param('VLAN_ID')
        vlan_spec_type = self.qualipy_helpers.get_user_param('VLAN_SPEC_TYPE')

        if not uuid:
            raise ValueError('VM_UUID is missing')

        if not vlan_id:
            raise ValueError('VLAN_ID is missing')

        if not vlan_spec_type:
            raise ValueError('VLAN_SPEC_TYPE is missing')

        # load default params
        dv_switch_path = self.vcenter_resource_model.default_dvswitch_path
        dv_switch_name = self.vcenter_resource_model.default_dvswitch_name
        port_group_path = self.vcenter_resource_model.default_port_group_path
        default_network = self.vcenter_resource_model.default_network

        vnic_to_network = VmNetworkMapping()
        vnic_to_network.dv_switch_path = dv_switch_path
        vnic_to_network.dv_switch_name = dv_switch_name
        vnic_to_network.port_group_path = port_group_path
        vnic_to_network.vlan_id = vlan_id
        vnic_to_network.vlan_spec = vlan_spec_type

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(
                connection_details,
                self.virtual_switch_connect_command.connect_to_networks,
                uuid,
                [vnic_to_network],
                default_network)

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
        uuid = self.qualipy_helpers.get_user_param('VM_UUID')
        resource_fullname = self.qualipy_helpers.get_user_param('RESOURCE_FULLNAME')

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(
                connection_details,
                self.destroyVirtualMachineCommand.destroy,
                uuid,
                resource_fullname)

    def deploy_from_template(self):
        # get command parameters from the environment
        deployment_params = self.qualipy_helpers.get_user_param('DEPLOY_DATA')
        data = self.serializer.decode(deployment_params)
        data_holder = DeployDataHolder(data)

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        result = self.command_wrapper.execute_command_with_connection(
                connection_details,
                self.deployFromTemplateCommand.execute_deploy_from_template,
                data_holder)

        print self._prepare_command_result(self.serializer.encode(result, unpicklable=False))

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

    def _prepare_command_result(self, output):
        return self.COMMAND_RESULT_PREFIX + str(output) + self.COMMAND_RESULT_POSTFIX
