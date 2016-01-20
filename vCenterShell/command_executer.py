﻿from models.DeployDataHolder import DeployDataHolder
from vCenterShell.vm.dvswitch_connector import VmNetworkMapping
from common.utilites.command_result import set_command_result


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
        connection_results = self.command_wrapper.execute_command_with_connection(connection_details,
                                                                                  self.virtual_switch_connect_command.connect_to_networks,
                                                                                  uuid,
                                                                                  [vnic_to_network],
                                                                                  default_network)
        set_command_result(result=connection_results, unpicklable=False)

    def disconnect_all(self):
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(
                connection_details,
                self.virtual_switch_disconnect_command.disconnect_all,
                vm_uuid)

    def disconnect(self):
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')
        network_name = self.qualipy_helpers.get_user_param('NETWORK_NAME')

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(
                connection_details,
                self.virtual_switch_disconnect_command.disconnect,
                vm_uuid,
                network_name)

    def destroy_vm(self):
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

        set_command_result(result=result, unpicklable=False)

    def power_off(self):
        # get command parameters from the environment
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')
        resource_fullname = self.qualipy_helpers.get_user_param('RESOURCE_FULLNAME')

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(connection_details,
                                                             self.vm_power_management_command.power_off,
                                                             vm_uuid,
                                                             resource_fullname)

    def power_on(self):
        # get command parameters from the environment
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')
        resource_fullname = self.qualipy_helpers.get_user_param('RESOURCE_FULLNAME')

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(connection_details,
                                                             self.vm_power_management_command.power_on,
                                                             vm_uuid,
                                                             resource_fullname)

    def refresh_ip(self):
        # get command parameters from the environment
        vm_uuid = self.qualipy_helpers.get_user_param('VM_UUID')
        resource_name = self.qualipy_helpers.get_user_param('RESOURCE_FULLNAME')

        # prepare for execute command
        connection_details = self.connection_retriever.connection_details()

        # execute command
        self.command_wrapper.execute_command_with_connection(connection_details,
                                                             self.refresh_ip_command.refresh_ip,
                                                             vm_uuid,
                                                             resource_name)
