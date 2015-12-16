from commands.DeployFromTemplateCommand import *
from commands.DestroyVirtualMachineCommand import DestroyVirtualMachineCommand
from pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService
from pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from pycommon.pyVmomiService import *
from vCenterShell.commands.DestroyVirtualMachineCommand import *


class CommandExecuterService(object):
    """ main class that publishes all available commands """

    def __init__(self, py_vmomi_service, network_adapter_retriever_command):
        :param py_vmomi_service:  PyVmomi service
        :param network_adapter_retriever_command:  Network adapter retriever command
        self.pyVmomiService = py_vmomi_service
        self.networkAdapterRetrieverCommand = network_adapter_retriever_command
        self.resource_connection_details_retriever = ResourceConnectionDetailsRetriever(self.cs_data_retriever_service)

    def deploy(self):
        DeployFromTemplateCommand(
                self.pyVmomiService,
                self.cs_data_retriever_service,
                self.resource_connection_details_retriever) \
            .execute()

    def destroy(self):
        DestroyVirtualMachineCommand(
                self.pyVmomiService,
                self.cs_data_retriever_service,
                self.resource_connection_details_retriever) \
            .execute()

    def connect(self):
        self.networkAdapterRetrieverCommand.execute()
