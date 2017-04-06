import time
from datetime import datetime, date
import jsonpickle
from cloudshell.cp.vcenter.models.OrchestrationSaveResult import OrchestrationSaveResult
from cloudshell.cp.vcenter.models.OrchestrationSavedArtifactsInfo import OrchestrationSavedArtifactsInfo
from cloudshell.cp.vcenter.models.OrchestrationSavedArtifact import OrchestrationSavedArtifact
from pyVim.connect import SmartConnect, Disconnect

from cloudshell.cp.vcenter.commands.connect_dvswitch import VirtualSwitchConnectCommand
from cloudshell.cp.vcenter.commands.connect_orchestrator import ConnectionCommandOrchestrator
from cloudshell.cp.vcenter.commands.deploy_vm import DeployCommand
from cloudshell.cp.vcenter.commands.destroy_vm import DestroyVirtualMachineCommand
from cloudshell.cp.vcenter.commands.disconnect_dvswitch import VirtualSwitchToMachineDisconnectCommand
from cloudshell.cp.vcenter.commands.load_vm import VMLoader
from cloudshell.cp.vcenter.commands.power_manager_vm import VirtualMachinePowerManagementCommand
from cloudshell.cp.vcenter.commands.refresh_ip import RefreshIpCommand
from cloudshell.cp.vcenter.commands.restore_snapshot import SnapshotRestoreCommand
from cloudshell.cp.vcenter.commands.modify_hardware import ModifyHardwareCommand
from cloudshell.cp.vcenter.commands.save_snapshot import SaveSnapshotCommand
from cloudshell.cp.vcenter.commands.retrieve_snapshots import RetrieveSnapshotsCommand
from cloudshell.cp.vcenter.common.cloud_shell.driver_helper import CloudshellDriverHelper
from cloudshell.cp.vcenter.common.cloud_shell.resource_remover import CloudshellResourceRemover
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.cp.vcenter.common.utilites.command_result import set_command_result, get_result_from_command_output
from cloudshell.cp.vcenter.common.utilites.common_name import generate_unique_name
from cloudshell.cp.vcenter.common.utilites.common_utils import back_slash_to_front_converter
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
from cloudshell.cp.vcenter.vm.ip_manager import VMIPManager
from cloudshell.cp.vcenter.vm.portgroup_configurer import VirtualMachinePortGroupConfigurer
from cloudshell.cp.vcenter.vm.vnic_to_network_mapper import VnicToNetworkMapper


class CommandOrchestrator(object):
    def __init__(self):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        in here the driver is going to be bootstrapped

        :param context: models.QualiDriverModels.InitCommandContext
        """
        self.cs_helper = CloudshellDriverHelper()
        synchronous_task_waiter = SynchronousTaskWaiter()
        pv_service = pyVmomiService(connect=SmartConnect, disconnect=Disconnect, task_waiter=synchronous_task_waiter)
        self.resource_model_parser = ResourceModelParser()
        port_group_name_generator = DvPortGroupNameGenerator()

        vnic_to_network_mapper = VnicToNetworkMapper(quali_name_generator=port_group_name_generator)
        resource_remover = CloudshellResourceRemover()
        ovf_service = OvfImageDeployerService(self.resource_model_parser)

        self.vm_loader = VMLoader(pv_service)

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

        ip_manager = VMIPManager()

        # Refresh IP command
        self.refresh_ip_command = RefreshIpCommand(pyvmomi_service=pv_service,
                                                   resource_model_parser=ResourceModelParser(),
                                                   ip_manager=ip_manager)

        # Save Snapshot
        self.snapshot_saver = SaveSnapshotCommand(pyvmomi_service=pv_service,
                                                  task_waiter=synchronous_task_waiter)

        # Snapshot Restorer
        self.snapshot_restorer = SnapshotRestoreCommand(pyvmomi_service=pv_service,
                                                        task_waiter=synchronous_task_waiter)

        self.snapshots_retriever = RetrieveSnapshotsCommand(pyvmomi_service=pv_service)

        self.hardware_modifier = ModifyHardwareCommand(pyvmomi_service=pv_service,
                                                       task_waiter=synchronous_task_waiter,
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
    def destroy_vm_only(self, context, ports):
        """
        Destroy Vm Command, will only destroy the vm and will not remove the resource

        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        resource_details = self._parse_remote_model(context)
        # execute command
        res = self.command_wrapper.execute_command_with_connection(
            context,
            self.destroy_virtual_machine_command.destroy_vm_only,
            resource_details.vm_uuid,
            resource_details.fullname)
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
                                                                   cancellation_context,
                                                                   context.remote_endpoints[0].app_context.app_request_json)
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

    def get_vm_uuid_by_name(self, context, vm_name):
        res = self.command_wrapper.execute_command_with_connection(context,
                                                                   self.vm_loader.load_vm_uuid_by_name,
                                                                   vm_name)
        return set_command_result(result=res, unpicklable=False)

    def modify_vm_hardware(self, context, vm_changes):
        resource_details = self._parse_remote_model(context)
        result = self.command_wrapper.execute_command_with_connection(context,
                                                                      self.hardware_modifier.modify_vm_hardware,
                                                                      resource_details.vm_uuid,
                                                                      vm_changes)
        return set_command_result(result=result, unpicklable=False)

    def save_snapshot(self, context, snapshot_name):
        """
        Saves virtual machine to a snapshot
        :param context: resource context of the vCenterShell
        :type context: models.QualiDriverModels.ResourceCommandContext
        :param snapshot_name: snapshot name to save to
        :type snapshot_name: str
        :return:
        """
        resource_details = self._parse_remote_model(context)
        created_snapshot_path = self.command_wrapper.execute_command_with_connection(context,
                                                                                     self.snapshot_saver.save_snapshot,
                                                                                     resource_details.vm_uuid,
                                                                                     snapshot_name)
        return set_command_result(created_snapshot_path)

    def restore_snapshot(self, context, snapshot_name):
        """
        Restores virtual machine from a snapshot
        :param context: resource context of the vCenterShell
        :type context: models.QualiDriverModels.ResourceCommandContext
        :param snapshot_name: snapshot name to save to
        :type snapshot_name: str
        :return:
        """
        resource_details = self._parse_remote_model(context)
        self.command_wrapper.execute_command_with_connection(context,
                                                             self.snapshot_restorer.restore_snapshot,
                                                             resource_details.vm_uuid,
                                                             resource_details.fullname,
                                                             snapshot_name)

    def get_snapshots(self, context):
        """
        Returns list of snapshots
        :param context: resource context of the vCenterShell
        :type context: models.QualiDriverModels.ResourceCommandContext
        :return:
        """
        resource_details = self._parse_remote_model(context)
        res = self.command_wrapper.execute_command_with_connection(context,
                                                                   self.snapshots_retriever.get_snapshots,
                                                                   resource_details.vm_uuid)
        return set_command_result(result=res, unpicklable=False)

    def orchestration_save(self, context, mode="shallow", custom_params=None):
        """
        Creates a snapshot with a unique name and returns SavedResults as JSON
        :param context: resource context of the vCenterShell
        :param mode: Snapshot save mode, default shallow. Currently not it use
        :param custom_params: Set of custom parameter to be supported in the future
        :return: SavedResults serialized as JSON
        :rtype: SavedResults
        """
        resource_details = self._parse_remote_model(context)
        created_date = datetime.now()
        snapshot_name = created_date.strftime('%y_%m_%d %H_%M_%S_%f')
        created_snapshot_path = self.save_snapshot(context=context, snapshot_name=snapshot_name)

        created_snapshot_path = self._strip_double_quotes(created_snapshot_path)

        orchestration_saved_artifact = OrchestrationSavedArtifact()
        orchestration_saved_artifact.artifact_type = 'vcenter_snapshot'
        orchestration_saved_artifact.identifier = created_snapshot_path

        saved_artifacts_info = OrchestrationSavedArtifactsInfo(
            resource_name=resource_details.cloud_provider,
            created_date=created_date,
            restore_rules={'requires_same_resource': True},
            saved_artifact=orchestration_saved_artifact)

        orchestration_save_result = OrchestrationSaveResult(saved_artifacts_info)

        return set_command_result(result=orchestration_save_result, unpicklable=False)

    @staticmethod
    def _strip_double_quotes(created_snapshot_path):
        if created_snapshot_path.startswith('"') and created_snapshot_path.endswith('"'):
            created_snapshot_path = created_snapshot_path[1:-1]
        return created_snapshot_path

    def orchestration_restore(self, context, saved_details):
        """

        :param context:
        :param saved_details:
        :return:
        """
        saved_artifacts_info = get_result_from_command_output(saved_details)
        snapshot_name = saved_artifacts_info['saved_artifacts_info']['saved_artifact']['identifier']
        return self.restore_snapshot(context=context, snapshot_name=snapshot_name)
