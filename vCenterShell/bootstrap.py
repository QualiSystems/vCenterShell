import jsonpickle
import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVim.connect import SmartConnect, Disconnect

from common.cloudshell.resource_creator import CloudshellResourceCreator
from common.logger import getLogger
from common.model_factory import ResourceModelParser
from common.cloudshell.conn_details_retriever import ResourceConnectionDetailsRetriever
from common.cloudshell.data_retriever import CloudshellDataRetrieverService
from common.utilites.common_name import generate_unique_name
from common.vcenter.task_waiter import SynchronousTaskWaiter
from common.vcenter.vmomi_service import pyVmomiService
from common.wrappers.command_wrapper import CommandWrapper
from vCenterShell.command_executer import CommandExecuterService
from vCenterShell.commands.refresh_ip import RefreshIpCommand
from vCenterShell.commands.connect_dvswitch import VirtualSwitchConnectCommand
from vCenterShell.commands.deploy_vm import DeployFromTemplateCommand
from vCenterShell.commands.destroy_vm import DestroyVirtualMachineCommand
from vCenterShell.commands.disconnect_dvswitch import VirtualSwitchToMachineDisconnectCommand
from vCenterShell.commands.power_manager_vm import VirtualMachinePowerManagementCommand
from vCenterShell.network.dvswitch.creator import DvPortGroupCreator
from vCenterShell.network.dvswitch.name_generator import DvPortGroupNameGenerator
from vCenterShell.network.vlan.factory import VlanSpecFactory
from vCenterShell.network.vlan.range_parser import VLanIdRangeParser
from vCenterShell.vm.deploy import VirtualMachineDeployer
from vCenterShell.vm.dvswitch_connector import VirtualSwitchToMachineConnector
from vCenterShell.vm.portgroup_configurer import VirtualMachinePortGroupConfigurer


class Bootstrapper(object):
    def __init__(self):
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cloudshell_data_retriever_service = CloudshellDataRetrieverService()
        resource_connection_details_retriever = ResourceConnectionDetailsRetriever(cloudshell_data_retriever_service)
        name_generator = generate_unique_name
        template_deployer = VirtualMachineDeployer(py_vmomi_service, name_generator)
        cloudshell_resource_creater = CloudshellResourceCreator(helpers)

        deploy_from_template_command = DeployFromTemplateCommand(template_deployer,
                                                                 cloudshell_resource_creater)

        destroy_virtual_machine_command = DestroyVirtualMachineCommand(py_vmomi_service,
                                                                       cloudshell_data_retriever_service)

        # Virtual Switch Connect
        synchronous_task_waiter = SynchronousTaskWaiter()
        dv_port_group_creator = DvPortGroupCreator(py_vmomi_service, synchronous_task_waiter)
        virtual_machine_port_group_configurer = VirtualMachinePortGroupConfigurer(py_vmomi_service,
                                                                                  synchronous_task_waiter)
        virtual_switch_to_machine_connector = VirtualSwitchToMachineConnector(py_vmomi_service,
                                                                              resource_connection_details_retriever,
                                                                              dv_port_group_creator,
                                                                              virtual_machine_port_group_configurer)

        resource_model_parser = ResourceModelParser()

        virtual_switch_connect_command = VirtualSwitchConnectCommand(cloudshell_data_retriever_service,
                                                                     virtual_switch_to_machine_connector,
                                                                     DvPortGroupNameGenerator(),
                                                                     VlanSpecFactory(),
                                                                     VLanIdRangeParser(),
                                                                     resource_model_parser)

        # Virtual Switch Revoke
        virtual_switch_disconnect_command = \
            VirtualSwitchToMachineDisconnectCommand(pyVmomiService,
                                                    cloudshell_data_retriever_service,
                                                    synchronous_task_waiter)

        # Power Command
        vm_power_management_command = VirtualMachinePowerManagementCommand(pyVmomiService,
                                                                           synchronous_task_waiter,
                                                                           helpers)
        # Refresh IP command
        refresh_ip_command = RefreshIpCommand(pyVmomiService, cloudshell_data_retriever_service, helpers,
                                              resource_model_parser)

        self.commandExecuterService = CommandExecuterService(jsonpickle,
                                                             helpers,
                                                             getLogger,
                                                             py_vmomi_service,
                                                             CommandWrapper,
                                                             resource_connection_details_retriever,
                                                             destroy_virtual_machine_command,
                                                             deploy_from_template_command,
                                                             virtual_switch_connect_command,
                                                             virtual_switch_disconnect_command,
                                                             vm_power_management_command,
                                                             refresh_ip_command)

    def get_command_executer_service(self):
        return self.commandExecuterService
