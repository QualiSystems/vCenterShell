import jsonpickle
from pyVim.connect import SmartConnect, Disconnect

from common.cloudshell.driver_helper import CloudshellDriverHelper
from common.cloudshell.resource_remover import CloudshellResourceRemover
from common.logger import getLogger
from common.model_factory import ResourceModelParser
from common.utilites.command_result import set_command_result
from common.utilites.common_name import generate_unique_name
from common.vcenter.task_waiter import SynchronousTaskWaiter
from common.vcenter.vmomi_service import pyVmomiService
from common.wrappers.command_wrapper import CommandWrapper
from models.DeployDataHolder import DeployDataHolder
from vCenterShell.commands.connect_dvswitch import VirtualSwitchConnectCommand
from vCenterShell.commands.deploy_vm import DeployFromTemplateCommand
from vCenterShell.commands.destroy_vm import DestroyVirtualMachineCommand
from vCenterShell.commands.disconnect_dvswitch import VirtualSwitchToMachineDisconnectCommand
from vCenterShell.commands.power_manager_vm import VirtualMachinePowerManagementCommand
from vCenterShell.commands.refresh_ip import RefreshIpCommand
from vCenterShell.network.dvswitch.creator import DvPortGroupCreator
from vCenterShell.network.dvswitch.name_generator import DvPortGroupNameGenerator
from vCenterShell.network.vlan.factory import VlanSpecFactory
from vCenterShell.network.vlan.range_parser import VLanIdRangeParser
from vCenterShell.network.vnic.vnic_service import VNicService
from vCenterShell.vm.deploy import VirtualMachineDeployer
from vCenterShell.vm.dvswitch_connector import VirtualSwitchToMachineConnector, VmNetworkMapping
from vCenterShell.vm.portgroup_configurer import VirtualMachinePortGroupConfigurer
from vCenterShell.vm.vnic_to_network_mapper import VnicToNetworkMapper


class VCenterShellDriver:

    def __init__(self):
        """
        ctor mast be without arguments, it is created with reflection at run time
        """
        self.cs_helper = None
        self.refresh_ip_command = None
        self.command_wrapper = None
        self.vc_data_model = None
        self.destroy_virtual_machine_command = None
        self.deploy_from_template_command = None
        self.virtual_switch_connect_command = None
        self.virtual_switch_disconnect_command = None
        self.vm_power_management_command = None

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        in here the driver is going to be bootstrapped

        :param context: models.QualiDriverModels.InitCommandContext
        """
        self.init(context)

    def init(self, context):
        self.cs_helper = CloudshellDriverHelper()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        synchronous_task_waiter = SynchronousTaskWaiter()
        resource_model_parser = ResourceModelParser()
        port_group_name_generator = DvPortGroupNameGenerator()
        self.vc_data_model = resource_model_parser.convert_to_resource_model(context.resource)
        vnic_to_network_mapper = VnicToNetworkMapper(quali_name_generator=port_group_name_generator)
        resource_remover = CloudshellResourceRemover()
        template_deployer = VirtualMachineDeployer(pv_service=pv_service, name_generator=generate_unique_name)
        dv_port_group_creator = DvPortGroupCreator(pyvmomi_service=pv_service,
                                                   synchronous_task_waiter=synchronous_task_waiter)
        virtual_machine_port_group_configurer = \
            VirtualMachinePortGroupConfigurer(pyvmomi_service=pv_service,
                                              synchronous_task_waiter=synchronous_task_waiter,
                                              vnic_to_network_mapper=vnic_to_network_mapper,
                                              vnic_service=VNicService())
        virtual_switch_to_machine_connector = VirtualSwitchToMachineConnector(dv_port_group_creator,
                                                                              virtual_machine_port_group_configurer)
        # Command Wrapper
        self.command_wrapper = CommandWrapper(logger=getLogger, pv_service=pv_service)
        # Deploy Command
        self.deploy_from_template_command = DeployFromTemplateCommand(deployer=template_deployer)
        # Virtual Switch Connect
        self.virtual_switch_connect_command = \
            VirtualSwitchConnectCommand(
                pv_service=pv_service,
                virtual_switch_to_machine_connector=virtual_switch_to_machine_connector,
                dv_port_group_name_generator=DvPortGroupNameGenerator(),
                vlan_spec_factory=VlanSpecFactory(),
                vlan_id_range_parser=VLanIdRangeParser(),
                logger=getLogger('VirtualSwitchConnectCommand'))
        # Virtual Switch Revoke
        self.virtual_switch_disconnect_command = \
            VirtualSwitchToMachineDisconnectCommand(
                pyvmomi_service=pv_service,
                port_group_configurer=virtual_machine_port_group_configurer,
                default_network=self.vc_data_model.default_network)
        # Destroy VM Command
        self.destroy_virtual_machine_command = \
            DestroyVirtualMachineCommand(pv_service=pv_service,
                                         resource_remover=resource_remover,
                                         disconnector=self.virtual_switch_disconnect_command)
        # Power Command
        self.vm_power_management_command = \
            VirtualMachinePowerManagementCommand(pyvmomi_service=pv_service,
                                                 synchronous_task_waiter=synchronous_task_waiter)
        # Refresh IP command
        self.refresh_ip_command = RefreshIpCommand(pyvmomi_service=pv_service)

    def connect(self, context, vm_uuid, vlan_id, vlan_spec_type):
        """
        Connect Command: connect a vm to a vlan, chooses the first available vnic

        :param context: models.QualiDriverModels.ResourceCommandContext
        :param str vm_uuid: the uuid id of the  vm
        :param str vlan_id: the id of the vlan, can be numeric or numeric range
        :param str vlan_spec_type: the type of the vlan, can only be ('Trunk', 'Access')

        :return str the connection details
        """
        # get command parameters from the environment
        if not vm_uuid:
            raise ValueError('VM_UUID is missing')

        if not vlan_id:
            raise ValueError('VLAN_ID is missing')

        if not vlan_spec_type:
            raise ValueError('VLAN_SPEC_TYPE is missing')

        # load default params
        vnic_to_network = VmNetworkMapping()
        vnic_to_network.dv_switch_path = self.vc_data_model.default_dvswitch_path
        vnic_to_network.dv_switch_name = self.vc_data_model.default_dvswitch_name
        vnic_to_network.port_group_path = self.vc_data_model.default_port_group_path
        vnic_to_network.vlan_id = vlan_id
        vnic_to_network.vlan_spec = vlan_spec_type

        # get connection details
        session = self.cs_helper.get_session(context)
        connection_details = self.cs_helper.get_connection_details(session, context)

        # execute command
        connection_results = \
            self.command_wrapper.execute_command_with_connection(connection_details,
                                                                 self.virtual_switch_connect_command.connect_to_networks,
                                                                 vm_uuid,
                                                                 [vnic_to_network],
                                                                 self.vc_data_model.default_network)
        return set_command_result(result=connection_results, unpicklable=False)

    def disconnect_all(self, context, vm_uuid):
        """
        Disconnect All Command, will the assign all the vnics on the vm to the default network,
        which is sign to be disconnected

        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str vm_uuid: vm uuid
        """
        if not vm_uuid:
            raise ValueError('VM_UUID is missing')

        # get connection details
        session = self.cs_helper.get_session(context)
        connection_details = self.cs_helper.get_connection_details(session, context)

        # execute command
        self.command_wrapper.execute_command_with_connection(
            connection_details,
            self.virtual_switch_disconnect_command.disconnect_all,
            vm_uuid)

    def disconnect(self, context, vm_uuid, network_name):
        """
        Disconnect Command, will disconnect the a specific network that is assign to the vm,
        the command will assign the default network for all the vnics that is assigned to the given network

        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str vm_uuid: the uuid of the vm
        :param str network_name: the name of the network to disconnect
        """

        # get connection details
        session = self.cs_helper.get_session(context)
        connection_details = self.cs_helper.get_connection_details(session, context)

        # execute command
        self.command_wrapper.execute_command_with_connection(
            connection_details,
            self.virtual_switch_disconnect_command.disconnect,
            vm_uuid,
            network_name)

    def destroy_vm(self, context, vm_uuid, vm_full_name):
        """
        Destroy Vm Command, will destroy the vm and remove the resource

        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str vm_uuid: the vm uuid to destroy
        """
        # get connection details
        session = self.cs_helper.get_session(context)
        connection_details = self.cs_helper.get_connection_details(session, context)

        # execute command
        self.command_wrapper.execute_command_with_connection(
            connection_details,
            self.destroy_virtual_machine_command.destroy,
            session,
            vm_uuid,
            vm_full_name)

    def deploy_from_template(self, context, deploy_data):
        """
        Deploy From Template Commnand, will deploy vm from template

        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str deploy_data: represent a json of the parameters, example: {
                "template_model": {
                    "vCenter_resource_name": "QualiSB",
                    "vm_folder": "QualiSB/Raz",
                    "template_name": "2"
                },
                "vm_cluster_model": {
                    "cluster_name": "QualiSB Cluster",
                    "resource_pool": "IT"
                },
                "datastore_name": "eric ds cluster",
                "power_on": False
            }
        :return str deploy results
        """
        # get connection details
        session = self.cs_helper.get_session(context)
        connection_details = self.cs_helper.get_connection_details(session, context)

        # get command parameters from the environment
        data = jsonpickle.decode(deploy_data)
        data_holder = DeployDataHolder(data)

        # execute command
        result = self.command_wrapper.execute_command_with_connection(
            connection_details,
            self.deploy_from_template_command.execute_deploy_from_template,
            data_holder)

        return set_command_result(result=result, unpicklable=False)

    def power_off(self, context, vm_uuid, vm_full_name):
        """
        Power off Command, will turn off the vm
        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str vm_uuid: the vm uuid to turn off
        """
        # get connection details
        session = self.cs_helper.get_session(context)
        connection_details = self.cs_helper.get_connection_details(session, context)

        # execute command
        self.command_wrapper.execute_command_with_connection(connection_details,
                                                             self.vm_power_management_command.power_off,
                                                             session,
                                                             vm_uuid,
                                                             vm_full_name)

    def power_on(self, context, vm_uuid, vm_full_name):
        """
        Power on Command, will turn on the vm
        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str vm_uuid: the vm uuid to turn on
        """
        # get connection details
        session = self.cs_helper.get_session(context)
        connection_details = self.cs_helper.get_connection_details(session, context)

        # execute command
        self.command_wrapper.execute_command_with_connection(connection_details,
                                                             self.vm_power_management_command.power_on,
                                                             session,
                                                             vm_uuid,
                                                             vm_full_name)

    def refresh_ip(self, context, vm_uuid, vm_full_name):
        """
        Refresh IP Command, will refresh the ip of the vm and will update it on the resource
        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str vm_uuid: the vm uuid
        """
        # get connection details
        session = self.cs_helper.get_session(context)
        connection_details = self.cs_helper.get_connection_details(session, context)

        # execute command
        self.command_wrapper.execute_command_with_connection(connection_details,
                                                             self.refresh_ip_command.refresh_ip,
                                                             session,
                                                             vm_uuid,
                                                             vm_full_name,
                                                             self.vc_data_model.default_network)
