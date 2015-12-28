from pyVim.connect import SmartConnect, Disconnect
from pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService
from pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter
from pycommon.pyVmomiService import pyVmomiService
from vCenterShell.commands.CommandExecuterService import CommandExecuterService
from vCenterShell.commands.DeployFromTemplateCommand import DeployFromTemplateCommand
from vCenterShell.commands.DestroyVirtualMachineCommand import DestroyVirtualMachineCommand
from vCenterShell.commands.DvPortGroupCreator import DvPortGroupCreator
from vCenterShell.commands.DvPortGroupNameGenerator import DvPortGroupNameGenerator
from vCenterShell.commands.NetworkAdaptersRetriever import NetworkAdaptersRetrieverCommand
from vCenterShell.commands.VLanIdRangeParser import VLanIdRangeParser
from vCenterShell.commands.VirtualMachinePortGroupConfigurer import VirtualMachinePortGroupConfigurer
from vCenterShell.commands.VirtualMachinePowerManagementCommand import VirtualMachinePowerManagementCommand
from vCenterShell.commands.VirtualSwitchConnectCommand import VirtualSwitchConnectCommand
from vCenterShell.commands.VirtualSwitchToMachineConnector import VirtualSwitchToMachineConnector
from vCenterShell.commands.VirtualSwitchToMachineDisconnectCommand import VirtualSwitchToMachineDisconnectCommand
from vCenterShell.commands.VlanSpecFactory import VlanSpecFactory
import qualipy.scripts.cloudshell_scripts_helpers as helpers


class Bootstrapper(object):
    def __init__(self):
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

        # Virtual Switch Connect
        synchronous_task_waiter = SynchronousTaskWaiter()
        dv_port_group_creator = DvPortGroupCreator(py_vmomi_service, synchronous_task_waiter)
        virtual_machine_port_group_configurer = VirtualMachinePortGroupConfigurer(py_vmomi_service,
                                                                                  synchronous_task_waiter)
        virtual_switch_to_machine_connector = VirtualSwitchToMachineConnector(py_vmomi_service,
                                                                              resource_connection_details_retriever,
                                                                              dv_port_group_creator,
                                                                              virtual_machine_port_group_configurer)
        virtual_switch_connect_command = VirtualSwitchConnectCommand(cloudshell_data_retriever_service,
                                                                     virtual_switch_to_machine_connector,
                                                                     DvPortGroupNameGenerator(),
                                                                     VlanSpecFactory(),
                                                                     VLanIdRangeParser())

        # Virtual Switch Revoke
        virtual_switch_disconnect_command = \
            VirtualSwitchToMachineDisconnectCommand(pyVmomiService,
                                                    resource_connection_details_retriever,
                                                    synchronous_task_waiter)

        # Power Command
        vm_power_management_command = VirtualMachinePowerManagementCommand(pyVmomiService,
                                                                           resource_connection_details_retriever,
                                                                           synchronous_task_waiter,
                                                                           helpers)

        self.commandExecuterService = CommandExecuterService(py_vmomi_service,
                                                             network_adapter_retriever_command,
                                                             destroy_virtual_machine_command,
                                                             deploy_from_template_command,
                                                             virtual_switch_connect_command,
                                                             virtual_switch_disconnect_command,
                                                             vm_power_management_command)

    def get_command_executer_service(self):
        return self.commandExecuterService
