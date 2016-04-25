import time
import jsonpickle
from cloudshell.cp.vcenter.commands.connect_dvswitch import VirtualSwitchConnectCommand
from cloudshell.cp.vcenter.commands.connect_orchestrator import ConnectionCommandOrchestrator
from cloudshell.cp.vcenter.commands.deploy_vm import DeployCommand
from cloudshell.cp.vcenter.commands.destroy_vm import DestroyVirtualMachineCommand
from cloudshell.cp.vcenter.commands.disconnect_dvswitch import VirtualSwitchToMachineDisconnectCommand
from cloudshell.cp.vcenter.commands.power_manager_vm import VirtualMachinePowerManagementCommand
from cloudshell.cp.vcenter.commands.refresh_ip import RefreshIpCommand
from cloudshell.cp.vcenter.common.cloud_shell.driver_helper import CloudshellDriverHelper
from cloudshell.cp.vcenter.common.cloud_shell.resource_remover import CloudshellResourceRemover
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.cp.vcenter.common.utilites.command_result import set_command_result
from cloudshell.cp.vcenter.common.utilites.common_name import generate_unique_name
from cloudshell.cp.vcenter.common.utilites.context_based_logger_factory import ContextBasedLoggerFactory
from cloudshell.cp.vcenter.common.vcenter.ovf_service import OvfImageDeployerService
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.common.wrappers.command_wrapper import CommandWrapper
from cloudshell.cp.vcenter.models.DeployDataHolder import DeployDataHolder
from cloudshell.cp.vcenter.models.DriverResponse import DriverResponse, DriverResponseRoot
from cloudshell.cp.vcenter.models.GenericDeployedAppResourceModel import GenericDeployedAppResourceModel
from cloudshell.cp.vcenter.network.dvswitch.creator import DvPortGroupCreator
from cloudshell.cp.vcenter.network.dvswitch.name_generator import DvPortGroupNameGenerator
from cloudshell.cp.vcenter.network.vlan.factory import VlanSpecFactory
from cloudshell.cp.vcenter.network.vlan.range_parser import VLanIdRangeParser
from cloudshell.cp.vcenter.network.vnic.vnic_service import VNicService
from cloudshell.cp.vcenter.vm.deploy import VirtualMachineDeployer
from cloudshell.cp.vcenter.vm.dvswitch_connector import VirtualSwitchToMachineConnector
from cloudshell.cp.vcenter.vm.portgroup_configurer import VirtualMachinePortGroupConfigurer
from cloudshell.cp.vcenter.vm.vnic_to_network_mapper import VnicToNetworkMapper
from pyVim.connect import SmartConnect, Disconnect
from cloudshell.cp.vcenter.common.utilites.common_utils import back_slash_to_front_converter


class CommandOrchestrator(object):
    def __init__(self):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        in here the driver is going to be bootstrapped

        :param context: models.QualiDriverModels.InitCommandContext
        """
        self.cs_helper = CloudshellDriverHelper()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        synchronous_task_waiter = SynchronousTaskWaiter()
        self.resource_model_parser = ResourceModelParser()
        port_group_name_generator = DvPortGroupNameGenerator()

        vnic_to_network_mapper = VnicToNetworkMapper(quali_name_generator=port_group_name_generator)
        resource_remover = CloudshellResourceRemover()
        ovf_service = OvfImageDeployerService(self.resource_model_parser)

        vm_deployer = VirtualMachineDeployer(pv_service=pv_service,
                                             name_generator=generate_unique_name,
                                             ovf_service=ovf_service,
                                             cs_helper=self.cs_helper,
                                             resource_model_parser=ResourceModelParser())

        dv_port_group_creator = DvPortGroupCreator(pyvmomi_service=pv_service,
                                                   synchronous_task_waiter=synchronous_task_waiter)
        virtual_machine_port_group_configurer = \
            VirtualMachinePortGroupConfigurer(pyvmomi_service=pv_service,
                                              synchronous_task_waiter=synchronous_task_waiter,
                                              vnic_to_network_mapper=vnic_to_network_mapper,
                                              vnic_service=VNicService(),
                                              name_gen=port_group_name_generator)
        virtual_switch_to_machine_connector = VirtualSwitchToMachineConnector(dv_port_group_creator,
                                                                              virtual_machine_port_group_configurer)
        # Command Wrapper
        self.command_wrapper = CommandWrapper(pv_service=pv_service,
                                              cloud_shell_helper=self.cs_helper,
                                              resource_model_parser=self.resource_model_parser,
                                              context_based_logger_factory=ContextBasedLoggerFactory())
        # Deploy Command
        self.deploy_command = DeployCommand(deployer=vm_deployer)

        # Virtual Switch Revoke
        self.virtual_switch_disconnect_command = \
            VirtualSwitchToMachineDisconnectCommand(
                pyvmomi_service=pv_service,
                port_group_configurer=virtual_machine_port_group_configurer,
                resource_model_parser=self.resource_model_parser)

        # Virtual Switch Connect
        virtual_switch_connect_command = \
            VirtualSwitchConnectCommand(
                pv_service=pv_service,
                virtual_switch_to_machine_connector=virtual_switch_to_machine_connector,
                dv_port_group_name_generator=DvPortGroupNameGenerator(),
                vlan_spec_factory=VlanSpecFactory(),
                vlan_id_range_parser=VLanIdRangeParser())
        self.connection_orchestrator = ConnectionCommandOrchestrator(
            connector=virtual_switch_connect_command,
            disconnector=self.virtual_switch_disconnect_command,
            resource_model_parser=self.resource_model_parser)

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
        self.refresh_ip_command = RefreshIpCommand(pyvmomi_service=pv_service,
                                                   resource_model_parser=ResourceModelParser())

    def connect_bulk(self, context, request):
        results = self.command_wrapper.execute_command_with_connection(
            context,
            self.connection_orchestrator.connect_bulk,
            request)

        driver_response = DriverResponse()
        driver_response.actionResults = results
        driver_response_root = DriverResponseRoot()
        driver_response_root.driverResponse = driver_response
        return set_command_result(result=driver_response_root, unpicklable=False)

    def deploy_from_template(self, context, deploy_data):
        """
        Deploy From Template Command, will deploy vm from template

        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str deploy_data: represent a json of the parameters, example: {"template_resource_model": {"vm_location": "", "vcenter_name": "VMware vCenter", "refresh_ip_timeout": "600", "auto_delete": "True", "vm_storage": "", "auto_power_on": "True", "autoload": "True", "ip_regex": "", "auto_power_off": "True", "vcenter_template": "Alex\\test", "vm_cluster": "", "vm_resource_pool": "", "wait_for_ip": "True"}, "app_name": "Temp"}
        :return str deploy results
        """

        # get command parameters from the environment
        data = jsonpickle.decode(deploy_data)
        data_holder = DeployDataHolder(data)
        data_holder.template_resource_model.vcenter_template = \
            back_slash_to_front_converter(data_holder.template_resource_model.vcenter_template)

        # execute command
        result = self.command_wrapper.execute_command_with_connection(
            context,
            self.deploy_command.execute_deploy_from_template,
            data_holder)

        return set_command_result(result=result, unpicklable=False)

    def deploy_clone_from_vm(self, context, deploy_data):
        """
        Deploy Cloned VM From VM Command, will deploy vm from template

        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str deploy_data: represent a json of the parameters, example: {"template_resource_model": {"vm_location": "", "vcenter_name": "VMware vCenter", "refresh_ip_timeout": "600", "auto_delete": "True", "vm_storage": "", "auto_power_on": "True", "autoload": "True", "ip_regex": "", "auto_power_off": "True", "vcenter_template": "Alex\\test", "vm_cluster": "", "vm_resource_pool": "", "wait_for_ip": "True"}, "app_name": "Temp"}
        :return str deploy results
        """

        # get command parameters from the environment
        data = jsonpickle.decode(deploy_data)
        data_holder = DeployDataHolder(data)
        data_holder.template_resource_model.vcenter_vm = \
            back_slash_to_front_converter(data_holder.template_resource_model.vcenter_vm)

        # execute command
        result = self.command_wrapper.execute_command_with_connection(
            context,
            self.deploy_command.execute_deploy_clone_from_vm,
            data_holder)

        return set_command_result(result=result, unpicklable=False)

    def deploy_from_linked_clone(self, context, deploy_data):
        """
        Deploy Cloned VM From VM Command, will deploy vm from template

        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str deploy_data: represent a json of the parameters, example: {"template_resource_model": {"vm_location": "", "vcenter_name": "VMware vCenter", "refresh_ip_timeout": "600", "auto_delete": "True", "vm_storage": "", "auto_power_on": "True", "autoload": "True", "ip_regex": "", "auto_power_off": "True", "vcenter_template": "Alex\\test", "vm_cluster": "", "vm_resource_pool": "", "wait_for_ip": "True"}, "app_name": "Temp"}
        :return str deploy results
        """

        # get command parameters from the environment
        data = jsonpickle.decode(deploy_data)
        data_holder = DeployDataHolder(data)

        if not data_holder.template_resource_model.vcenter_vm:
            raise ValueError('Please insert vm to deploy from')

        data_holder.template_resource_model.vcenter_vm = \
            back_slash_to_front_converter(data_holder.template_resource_model.vcenter_vm)

        if not data_holder.template_resource_model.vcenter_vm_snapshot:
            raise ValueError('Please insert snapshot to deploy from')

        data_holder.template_resource_model.vcenter_vm_snapshot = \
            back_slash_to_front_converter(data_holder.template_resource_model.vcenter_vm_snapshot)

        # execute command
        result = self.command_wrapper.execute_command_with_connection(
            context,
            self.deploy_command.execute_deploy_from_linked_clone,
            data_holder)

        return set_command_result(result=result, unpicklable=False)

    def deploy_from_image(self, context, deploy_data):
        """
        Deploy From Image Command, will deploy vm from ovf image

        :param models.QualiDriverModels.ResourceCommandContext context: the context of the command
        :param str deploy_data: represent a json of the parameters, example: {
                "image_url": "c:\image.ovf" or
                             "\\nas\shared\image.ovf" or
                             "http://192.168.65.88/ovf/Debian%2064%20-%20Yoav.ovf",
                "cluster_name": "QualiSB Cluster",
                "resource_pool": "LiverPool",
                "datastore_name": "eric ds cluster",
                "datacenter_name": "QualiSB"
                "power_on": False
                "app_name": "appName"
                "user_arguments": ["--compress=9", " --schemaValidate", "--etc"]
            }
        :return str deploy results
        """
        # get command parameters from the environment
        data = jsonpickle.decode(deploy_data)
        data_holder = DeployDataHolder(data)

        # execute command
        result = self.command_wrapper.execute_command_with_connection(
            context,
            self.deploy_command.execute_deploy_from_image,
            data_holder,
            context.resource)

        return set_command_result(result=result, unpicklable=False)

    # remote command
    def disconnect_all(self, context, ports):
        """
        Disconnect All Command, will the assign all the vnics on the vm to the default network,
        which is sign to be disconnected

        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        resource_details = self._parse_remote_model(context)
        # execute command
        res = self.command_wrapper.execute_command_with_connection(
            context,
            self.virtual_switch_disconnect_command.disconnect_all,
            resource_details.vm_uuid)
        return set_command_result(result=res, unpicklable=False)

    # remote command
    def disconnect(self, context, ports, network_name):
        """
        Disconnect Command, will disconnect the a specific network that is assign to the vm,
        the command will assign the default network for all the vnics that is assigned to the given network

        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param str network_name: the name of the network to disconnect from
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        resource_details = self._parse_remote_model(context)
        # execute command
        res = self.command_wrapper.execute_command_with_connection(
            context,
            self.virtual_switch_disconnect_command.disconnect,
            resource_details.vm_uuid,
            network_name)
        return set_command_result(result=res, unpicklable=False)

    # remote command
    def destroy_vm(self, context, ports):
        """
        Destroy Vm Command, will destroy the vm and remove the resource

        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        resource_details = self._parse_remote_model(context)
        reservation_id = context.remote_reservation.reservation_id
        # execute command
        res = self.command_wrapper.execute_command_with_connection(
            context,
            self.destroy_virtual_machine_command.destroy,
            resource_details.vm_uuid,
            resource_details.fullname,
            reservation_id)
        return set_command_result(result=res, unpicklable=False)

    # remote command
    def destroy_vm_only(self, context, ports):
        """
        Destroy Vm Command, will only destroy the vm and will not remove the resource

        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        resource_details = self._parse_remote_model(context)
        reservation_id = context.remote_reservation.reservation_id
        # execute command
        res = self.command_wrapper.execute_command_with_connection(
            context,
            self.destroy_virtual_machine_command.destroy_vm_only,
            resource_details.vm_uuid,
            resource_details.fullname,
            reservation_id)
        return set_command_result(result=res, unpicklable=False)

    # remote command
    def refresh_ip(self, context, cancellation_context, ports):
        """
        Refresh IP Command, will refresh the ip of the vm and will update it on the resource
        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param cancellation_context:
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        resource_details = self._parse_remote_model(context)
        # execute command
        res = self.command_wrapper.execute_command_with_connection(context,
                                                                   self.refresh_ip_command.refresh_ip,
                                                                   resource_details.vm_uuid,
                                                                   resource_details.fullname,
                                                                   cancellation_context)
        return set_command_result(result=res, unpicklable=False)

    # remote command
    def power_off(self, context, ports):
        """
        Powers off the remote vm
        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        return self._power_command(context, ports, self.vm_power_management_command.power_off)

    # remote command
    def power_on(self, context, ports):
        """
        Powers on the remote vm
        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        return self._power_command(context, ports, self.vm_power_management_command.power_on)

    # remote command
    def power_cycle(self, context, ports, delay):
        """
        preforms a restart to the vm
        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        :param number delay: the time to wait between the power on and off
        """
        self.power_off(context, ports)
        time.sleep(float(delay))
        return self.power_on(context, ports)

    def _power_command(self, context, ports, command):
        resource_details = self._parse_remote_model(context)

        # execute command
        res = self.command_wrapper.execute_command_with_connection(context,
                                                                   command,
                                                                   resource_details.vm_uuid,
                                                                   resource_details.fullname)
        return set_command_result(result=res, unpicklable=False)

    def _parse_remote_model(self, context):
        """
        parse the remote resource model and adds its full name
        :type context: models.QualiDriverModels.ResourceRemoteCommandContext

        """
        if not context.remote_endpoints:
            raise Exception('no remote resources found in context: {0}', jsonpickle.encode(context, unpicklable=False))
        resource = context.remote_endpoints[0]

        dictionary = jsonpickle.decode(resource.app_context.deployed_app_json)
        holder = DeployDataHolder(dictionary)
        app_resource_detail = GenericDeployedAppResourceModel()
        app_resource_detail.vm_uuid = holder.vmdetails.uid
        app_resource_detail.cloud_provider = context.resource.fullname
        app_resource_detail.fullname = resource.fullname
        return app_resource_detail

    def power_on_not_roemote(self, context, vm_uuid, resource_fullname):
        # get connection details
        res = self.command_wrapper.execute_command_with_connection(context,
                                                                   self.vm_power_management_command.power_on,
                                                                   vm_uuid,
                                                                   resource_fullname)
        return set_command_result(result=res, unpicklable=False)
