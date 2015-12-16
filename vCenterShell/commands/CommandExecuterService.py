from vCenterShell.pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from vCenterShell.commands.DeployFromTemplateCommand import *
from vCenterShell.commands.destroyVirtualMachineCommand import *


class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self, py_vmomi_service, network_adapter_retriever_command):
        """
        :param py_vmomi_service:  PyVmomi service
        :param network_adapter_retriever_command:  Network adapter retriever command
        """
        self.pyVmomiService = py_vmomi_service
        self.networkAdapterRetrieverCommand = network_adapter_retriever_command

    def deploy(self):
        csDataRetrieverService = CloudshellDataRetrieverService()
        DeployFromTemplateCommand(self.pyVmomiService, csDataRetrieverService,
                                  ResourceConnectionDetailsRetriever(csDataRetrieverService)) \
            .execute()

    def destroy(self):
        DestroyVirtualMachineCommand(self.pyVmomiService) \
            .execute()

    def connect(self):
        self.networkAdapterRetrieverCommand.execute()
