import os
import qualipy.scripts.cloudshell_scripts_helpers as helpers



class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self,
                 py_vmomi_service,
                 destroy_virtual_machine_command,
                 deploy_from_template_command,
                 virtual_switch_connect_command,
                 virtual_switch_disconnect_command,
                 vm_power_management_command):
        """
        :param py_vmomi_service:  PyVmomi service
        :param network_adapter_retriever_command:  Network adapter retriever command
        """
        self.pyVmomiService = py_vmomi_service
        self.destroyVirtualMachineCommand = destroy_virtual_machine_command
        self.deployFromTemplateCommand = deploy_from_template_command
        self.virtual_switch_connect_command = virtual_switch_connect_command
        self.virtual_switch_disconnect_command = virtual_switch_disconnect_command
        self.vm_power_management_command = vm_power_management_command

    def deploy_from_template(self):
        self.deployFromTemplateCommand.execute_deploy_from_template()

    def deploy(self):
        self.deployFromTemplateCommand.execute()

    def destroy(self):
        self.disconnect_all()
        self.destroyVirtualMachineCommand.execute()

    def connect(self):
        vlan_id = helpers.get_user_param('VLAN_ID')
        vlan_spec_type = helpers.get_user_param('VLAN_SPEC_TYPE')
        self.virtual_switch_connect_command.connect_vm_to_vlan(vlan_id, vlan_spec_type)

    def disconnect_all(self):
        # todo: the vcenter param should be getting inside the command from resource
        vcener_name = helpers.get_user_param('VCENTER_NAME')
        virtual_machine_id = helpers.get_user_param('VM_UUID')
        self.virtual_switch_disconnect_command.disconnect_all(vcener_name, virtual_machine_id)

    def disconnect(self):
        # todo: the vcenter param should be getting inside the command from resource
        vcener_name = helpers.get_user_param('VCENTER_NAME')
        virtual_machine_id = helpers.get_user_param('VM_UUID')
        network_name = helpers.get_user_param('NETWORK_NAME')
        self.virtual_switch_disconnect_command.disconnect(vcener_name, virtual_machine_id, network_name)

    def power_off(self):
        vm_uuid = helpers.get_user_param('VM_UUID')
        self.vm_power_management_command.power_off(vm_uuid)

    def power_on(self):
        vm_uuid = helpers.get_user_param('VM_UUID')
        self.vm_power_management_command.power_on(vm_uuid)
