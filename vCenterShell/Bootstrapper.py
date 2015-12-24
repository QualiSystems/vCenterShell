from pyVim.connect import SmartConnect, Disconnect

from pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter
from pycommon.pyVmomiService import pyVmomiService
from pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService
from vCenterShell.commands.DvPortGroupCreator import DvPortGroupCreator
from vCenterShell.commands.DvPortGroupNameGenerator import DvPortGroupNameGenerator
from vCenterShell.commands.VirtualMachinePortGroupConfigurer import VirtualMachinePortGroupConfigurer
from vCenterShell.commands.VirtualSwitchConnectCommand import VirtualSwitchConnectCommand
from vCenterShell.commands.VirtualSwitchToMachineConnector import VirtualSwitchToMachineConnector
from vCenterShell.commands.VlanSpecFactory import VlanSpecFactory
from vCenterShell.commands.DestroyVirtualMachineCommand import DestroyVirtualMachineCommand
from vCenterShell.commands.CommandExecuterService import CommandExecuterService
from vCenterShell.commands.DeployFromTemplateCommand import DeployFromTemplateCommand
from vCenterShell.commands.NetworkAdaptersRetriever import NetworkAdaptersRetrieverCommand
from vCenterShell.commands.VirtualSwitchFromMachineRevoker import VirtualSwitchFromMachineRevoker
from vCenterShell.commands.VirtualSwitchRevokeCommand import VirtualSwitchRevokeCommand
from vCenterShell.commands.destroyVirtualMachineCommand import DestroyVirtualMachineCommand


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
        dv_port_group_creator = DvPortGroupCreator(pyVmomiService, synchronous_task_waiter)
        virtual_machine_port_group_configurer = VirtualMachinePortGroupConfigurer(pyVmomiService,
                                                                                  synchronous_task_waiter)
        virtual_switch_to_machine_connector = VirtualSwitchToMachineConnector(pyVmomiService,
                                                                              resource_connection_details_retriever,
                                                                              dv_port_group_creator,
                                                                              virtual_machine_port_group_configurer)
        virtual_switch_connect_command = VirtualSwitchConnectCommand(cloudshell_data_retriever_service,
                                                                    virtual_switch_to_machine_connector,
                                                                    DvPortGroupNameGenerator(),
                                                                    VlanSpecFactory())

        # Virtual Switch Revoke
        virtual_switch_from_machine_revoker = VirtualSwitchFromMachineRevoker(pyVmomiService,
                                                                            resource_connection_details_retriever,
                                                                            synchronous_task_waiter)

        virtual_switch_revoke_command = VirtualSwitchRevokeCommand(pyVmomiService,
                                                                   virtual_switch_from_machine_revoker,
                                                                   resource_connection_details_retriever,
                                                                   synchronous_task_waiter)

        self.commandExecuterService = CommandExecuterService(py_vmomi_service,
                                                             network_adapter_retriever_command,
                                                             destroy_virtual_machine_command,
                                                             deploy_from_template_command,
                                                             virtual_switch_connect_command,
                                                             virtual_switch_revoke_command)

    def get_command_executer_service(self):
        return self.commandExecuterService
