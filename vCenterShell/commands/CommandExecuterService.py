import os


class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self,
                 py_vmomi_service,
                 network_adapter_retriever_command,
                 destroy_virtual_machine_command,
                 deploy_from_template_command,
                 virtual_switch_connect_command,
                 virtual_switch_revoke_command):
        """
        :param py_vmomi_service:  PyVmomi service
        :param network_adapter_retriever_command:  Network adapter retriever command
        """
        self.pyVmomiService = py_vmomi_service
        self.networkAdapterRetrieverCommand = network_adapter_retriever_command
        self.destroyVirtualMachineCommand = destroy_virtual_machine_command
        self.deployFromTemplateCommand = deploy_from_template_command
        self.virtual_switch_connect_command = virtual_switch_connect_command
        self.virtual_switch_revoke_command = virtual_switch_revoke_command

    def deploy_from_template(self):
        self.deployFromTemplateCommand.execute_deploy_from_template()

    def deploy(self):
        self.deployFromTemplateCommand.execute()

    def destroy(self):
        self.revoke()
        self.destroyVirtualMachineCommand.execute()

    def connect(self):
        vlan_id = os.environ.get('VLAN_ID')
        vlan_spec_type = os.environ.get('VLAN_SPEC_TYPE')
        self.virtual_switch_connect_command.connect_vm_to_vlan(vlan_id, vlan_spec_type)

    def revoke(self):
        vlan_id = os.environ.get('VLAN_ID')
        vlan_spec_type = os.environ.get('VLAN_SPEC_TYPE')
        self.virtual_switch_revoke_command.revoke_vm_from_vlan(vlan_id, vlan_spec_type)


