from pyVim.connect import SmartConnect, Disconnect
from vCenterShell.commands.DeployFromTemplateCommand import DeployFromTemplateCommand
from vCenterShell.commands.destroyVirtualMachineCommand import DestroyVirtualMachineCommand
from vCenterShell.pycommon.pyVmomiService import pyVmomiService
from vCenterShell.commands.CommandExecuterService import CommandExecuterService
from vCenterShell.commands.NetworkAdaptersRetriever import NetworkAdaptersRetrieverCommand
from vCenterShell.pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService
from vCenterShell.pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from vCenterShell.pycommon.logging_service import LoggingService

class Bootstrapper(object):
    def __init__(self):
        LoggingService("DEBUG")
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cloudshell_data_retriever_service = CloudshellDataRetrieverService()
        resource_connection_details_retriever = ResourceConnectionDetailsRetriever(cloudshell_data_retriever_service)
        network_adapter_retriever_command = NetworkAdaptersRetrieverCommand(py_vmomi_service,
                                                                            cloudshell_data_retriever_service,
                                                                            resource_connection_details_retriever)
        destroy_virtual_machine_command = DestroyVirtualMachineCommand(py_vmomi_service,
                                                                       cloudshell_data_retriever_service)

        deploy_from_template_command = DeployFromTemplateCommand(py_vmomi_service, cloudshell_data_retriever_service,
                                                                 resource_connection_details_retriever)

        self.commandExecuterService = CommandExecuterService(py_vmomi_service,
                                                             network_adapter_retriever_command,
                                                             destroy_virtual_machine_command,
                                                             deploy_from_template_command)

    def get_command_executer_service(self):
        return self.commandExecuterService
