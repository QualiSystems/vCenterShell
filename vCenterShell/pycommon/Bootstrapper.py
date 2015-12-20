from pyVim.connect import SmartConnect, Disconnect

from commands.VirtualSwitchConnectCommand import VirtualSwitchConnectCommand
from vCenterShell.pycommon.pyVmomiService import pyVmomiService
from vCenterShell.commands.CommandExecuterService import CommandExecuterService
from vCenterShell.commands.NetworkAdaptersRetriever import NetworkAdaptersRetriever
from vCenterShell.pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService
from vCenterShell.pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever


class Bootstrapper(object):
    def __init__(self):
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cloudshell_data_retriever_service = CloudshellDataRetrieverService()
        resource_connection_details_retriever = ResourceConnectionDetailsRetriever(cloudshell_data_retriever_service)
        network_adapter_retriever_command = NetworkAdaptersRetriever(py_vmomi_service,
                                                                     cloudshell_data_retriever_service,
                                                                     resource_connection_details_retriever)
        virtual_switch_connect_command = VirtualSwitchConnectCommand(pyVmomiService, cloudshell_data_retriever_service,
                                                                     None, network_adapter_retriever_command)
        self.commandExecuterService = CommandExecuterService(py_vmomi_service, network_adapter_retriever_command,
                                                             virtual_switch_connect_command)

    def get_command_executer_service(self):
        return self.commandExecuterService
