from pyVim.connect import SmartConnect, Disconnect
from vCenterShell.commands.destroyVirtualMachineCommand import DestroyVirtualMachineCommand
from vCenterShell.pycommon.pyVmomiService import pyVmomiService
from vCenterShell.commands.CommandExecuterService import CommandExecuterService
from vCenterShell.commands.NetworkAdaptersRetrieverCommand import NetworkAdaptersRetrieverCommand
from vCenterShell.pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService
from vCenterShell.pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever


class Bootstrapper(object):
    def __init__(self):
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cloudshell_data_retriever_service = CloudshellDataRetrieverService()
        resource_connection_details_retriever = ResourceConnectionDetailsRetriever(cloudshell_data_retriever_service)
        network_adapter_retriever_command = NetworkAdaptersRetrieverCommand(py_vmomi_service,
                                                                            cloudshell_data_retriever_service,
                                                                            resource_connection_details_retriever)
        destroyVirtualMachineCommand = DestroyVirtualMachineCommand(py_vmomi_service, cloudshell_data_retriever_service)
        self.commandExecuterService = CommandExecuterService(py_vmomi_service, network_adapter_retriever_command, destroyVirtualMachineCommand)

    def get_command_executer_service(self):
        return self.commandExecuterService
