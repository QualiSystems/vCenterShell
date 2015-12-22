class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self, py_vmomi_service, network_adapter_retriever_command, destroy_virtual_machine_command,
                 deploy_from_template_command):
        """
        :param py_vmomi_service:  PyVmomi service
        :param network_adapter_retriever_command:  Network adapter retriever command
        """
        self.pyVmomiService = py_vmomi_service
        self.networkAdapterRetrieverCommand = network_adapter_retriever_command
        self.destroyVirtualMachineCommand = destroy_virtual_machine_command
        self.deployFromTemplateCommand = deploy_from_template_command

    def deploy_from_template(self):
        self.deployFromTemplateCommand.deploy_execute()

    def deploy(self):
        self.deployFromTemplateCommand.execute()

    def destroy(self):
        self.destroyVirtualMachineCommand.execute()

    def connect(self):
        self.networkAdapterRetrieverCommand.execute()
