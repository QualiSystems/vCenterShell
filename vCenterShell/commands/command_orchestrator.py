import copy
import time
import uuid
from logging import getLogger
from multiprocessing.pool import ThreadPool
import jsonpickle
from pyVim.connect import SmartConnect, Disconnect
from common.cloud_shell.driver_helper import CloudshellDriverHelper
from common.cloud_shell.resource_remover import CloudshellResourceRemover
from common.model_factory import ResourceModelParser
from common.utilites.command_result import set_command_result
from common.utilites.common_name import generate_unique_name
from common.vcenter.task_waiter import SynchronousTaskWaiter
from common.vcenter.vmomi_service import pyVmomiService
from common.wrappers.command_wrapper import CommandWrapper
from models.ActionResult import ActionResult
from models.DeployDataHolder import DeployDataHolder
from models.DriverResponse import DriverResponse, DriverResponseRoot
from vCenterShell.commands.combine_action import CombineAction
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
from vCenterShell.vm.dvswitch_connector import VirtualSwitchToMachineConnector, VmNetworkMapping, VmNetworkRemoveMapping
from vCenterShell.vm.portgroup_configurer import VirtualMachinePortGroupConfigurer
from vCenterShell.vm.vnic_to_network_mapper import VnicToNetworkMapper


class CommandOrchestrator(object):
    def __init__(self, context):
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
        self.vc_data_model = self.resource_model_parser.convert_to_resource_model(context.resource)
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

    def _group_actions_by_uuid_and_mode(self, actions):
        key_to_actions = dict()

        # group by machine and vlan mode and action type
        for action in actions:
            vm_uuid = self._get_vm_uuid(action)
            vlan_mode = action.connectionParams.mode
            action_type = action.type
            key = (vm_uuid, vlan_mode, action_type)
            if key not in key_to_actions:
                key_to_actions[key] = []
            key_to_actions[key].append(action)

        # generate new keys
        return {uuid.uuid4(): action
                for key, action in key_to_actions}

    def _create_new_action_by_mapping(self, mapping):
        actions = []

        for key, actions_arr in mapping.items():
            action = copy.deepcopy(actions_arr[0])
            action.actionId = key
            for act in actions_arr[1:]:
                CombineAction.combine(action, act)
            actions.append(action)
        return actions

    def connect_bulk(self, context, request):
        dv_switch_path = self.vc_data_model.default_dvswitch_path
        dv_switch_name = self.vc_data_model.default_dvswitch_name
        port_group_path = self.vc_data_model.default_port_group_path
        default_network = self.vc_data_model.default_network

        holder = DeployDataHolder(jsonpickle.decode(request))

        results = []
        session = self.cs_helper.get_session(context.connectivity.server_address, context.connectivity.admin_auth_token,
                                             context.reservation.domain)
        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        pool = ThreadPool()
        async_results = []

        mappings = self._group_actions_by_uuid_and_mode(holder.driverRequest.actions, session)
        unified_actions = self._create_new_action_by_mapping(mappings)

        for key, action in unified_actions.items():
            vm_uuid = self._get_vm_uuid(action)
            if action.type == 'setVlan':
                res = pool.apply_async(self._set_vlan_bulk,
                                       (action, default_network, dv_switch_name, dv_switch_path,
                                        port_group_path,
                                        vm_uuid, connection_details))

            elif action.type == 'removeVlan':

                res = pool.apply_async(self._remove_vlan_bulk,
                                       (action, default_network, vm_uuid, connection_details))

            if res:
                async_results.append(res)

        for async_result in async_results:
            action_results = async_result.get()
            for action_result in action_results:
                for unified_action in unified_actions[action_results.actionId]:
                    copied_action = copy.deepcopy(action_result)
                    copied_action.actionId = unified_action.actionId
                    results.append(copied_action)

        driver_response = DriverResponse()
        driver_response.actionResults = results
        driver_response_root = DriverResponseRoot()
        driver_response_root.driverResponse = driver_response
        return set_command_result(result=driver_response_root, unpicklable=False)

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
        session = self.cs_helper.get_session(context.connectivity.server_address, context.connectivity.admin_auth_token,
                                             context.reservation.domain)
        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        # get command parameters from the environment
        data = jsonpickle.decode(deploy_data)
        data_holder = DeployDataHolder(data)

        # execute command
        result = self.command_wrapper.execute_command_with_connection(
            connection_details,
            self.deploy_from_template_command.execute_deploy_from_template,
            data_holder)

        return set_command_result(result=result, unpicklable=False)

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
        session = self.cs_helper.get_session(context.connectivity.server_address, context.connectivity.admin_auth_token,
                                             context.reservation.domain)
        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        # execute command
        connection_results = \
            self.command_wrapper.execute_command_with_connection(
                connection_details,
                self.virtual_switch_connect_command.connect_to_networks,
                vm_uuid,
                [vnic_to_network],
                self.vc_data_model.default_network)

        return set_command_result(result=connection_results, unpicklable=False)

    # remote command
    def disconnect_all(self, context, ports):
        """
        Disconnect All Command, will the assign all the vnics on the vm to the default network,
        which is sign to be disconnected

        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        # get connection details
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.remote_reservation.domain)
        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        resource_details = self._parse_remote_model(context)

        # execute command
        res = self.command_wrapper.execute_command_with_connection(
            connection_details,
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

        # get connection details
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.remote_reservation.domain)
        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        resource_details = self._parse_remote_model(context)

        # execute command
        res = self.command_wrapper.execute_command_with_connection(
            connection_details,
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
        # get connection details
        session = self.cs_helper.get_session(context.connectivity.server_address, context.connectivity.admin_auth_token,
                                             context.remote_reservation.domain)
        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        resource_details = self._parse_remote_model(context)

        # execute command
        res = self.command_wrapper.execute_command_with_connection(
            connection_details,
            self.destroy_virtual_machine_command.destroy,
            session,
            resource_details.vm_uuid,
            resource_details.fullname)
        return set_command_result(result=res, unpicklable=False)

    # remote command
    def refresh_ip(self, context, ports):
        """
        Refresh IP Command, will refresh the ip of the vm and will update it on the resource

        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        # get connection details
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.remote_reservation.domain)
        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        resource_details = self._parse_remote_model(context)

        # execute command
        res = self.command_wrapper.execute_command_with_connection(connection_details,
                                                                   self.refresh_ip_command.refresh_ip,
                                                                   session,
                                                                   resource_details.vm_uuid,
                                                                   resource_details.fullname,
                                                                   self.vc_data_model.default_network)
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
        # get connection details
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.remote_reservation.domain)

        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        resource_details = self._parse_remote_model(context)

        # execute command
        res = self.command_wrapper.execute_command_with_connection(connection_details,
                                                                   command,
                                                                   session,
                                                                   resource_details.vm_uuid,
                                                                   resource_details.fullname)
        return set_command_result(result=res, unpicklable=False)

    def _get_vm_uuid(self, action):
        vm_uuid_values = [attr.attributeValue for attr in action.customActionAttributes
                          if attr.attributeName == 'VM_UUID']

        if vm_uuid_values and vm_uuid_values[0]:
            return vm_uuid_values[0]

        raise ValueError('VM_UUID is missing on action attributes')

    def _get_vnic_name(self, action):
        vnic_name_values = [attr.attributeValue for attr in action.customActionAttributes
                            if attr.attributeName == 'Vnic Name']
        if vnic_name_values:
            return vnic_name_values[0]
        return None

    def _parse_remote_model(self, context):
        """
        parse the remote resource model and adds its full name
        :type context: models.QualiDriverModels.ResourceRemoteCommandContext

        """
        if not context.remote_endpoints:
            raise Exception('no remote resources found in context: {0}', jsonpickle.encode(context, unpicklable=False))
        resource = context.remote_endpoints[0]
        resource_details = self.resource_model_parser.convert_to_resource_model(resource)
        resource_details.fullname = resource.fullname
        return resource_details

    def power_on_not_roemote(self, context, vm_uuid, resource_fullname):
        # get connection details
        session = self.cs_helper.get_session(context.connectivity.server_address, context.connectivity.admin_auth_token,
                                             context.reservation.domain)
        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        res = self.command_wrapper.execute_command_with_connection(connection_details,
                                                                   self.vm_power_management_command.power_on,
                                                                   session,
                                                                   vm_uuid,
                                                                   resource_fullname)
        return set_command_result(result=res, unpicklable=False)

    def refresh_ip(self, context, ports):
        """
        Refresh IP Command, will refresh the ip of the vm and will update it on the resource

        :param models.QualiDriverModels.ResourceRemoteCommandContext context: the context the command runs on
        :param list[string] ports: the ports of the connection between the remote resource and the local resource, NOT IN USE!!!
        """
        # get connection details
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.remote_reservation.domain)
        connection_details = self.cs_helper.get_connection_details(session, context.resource)

        resource_details = self._parse_remote_model(context)

        # execute command
        res = self.command_wrapper.execute_command_with_connection(connection_details,
                                                                   self.refresh_ip_command.refresh_ip,
                                                                   session,
                                                                   resource_details.vm_uuid,
                                                                   resource_details.fullname,
                                                                   self.vc_data_model.default_network)
        return set_command_result(result=res, unpicklable=False)

    def _set_vlan_bulk(self, action, default_network, dv_switch_name, dv_switch_path, port_group_path, vm_uuid,
                       connection_details):
        mappings = []
        results = []
        for vlan in action.connectionParams.vlanIds:
            vnic_to_network = VmNetworkMapping()
            vnic_to_network.dv_switch_path = dv_switch_path
            vnic_to_network.dv_switch_name = dv_switch_name
            vnic_to_network.port_group_path = port_group_path
            vnic_to_network.vlan_id = vlan
            vnic_to_network.vlan_spec = action.connectionParams.mode

            vnic_name = self._get_vnic_name(action)
            if vnic_name:
                vnic_to_network.vnic_name = vnic_name

            mappings.append(vnic_to_network)
        if mappings:
            try:
                connection_results = self.command_wrapper.execute_command_with_connection(connection_details,
                                                                                          self.virtual_switch_connect_command.connect_to_networks,
                                                                                          vm_uuid,
                                                                                          mappings,
                                                                                          default_network)
                for connection_result in connection_results:
                    result = ActionResult()
                    result.actionId = str(action.actionId)
                    result.type = str(action.type)
                    result.infoMessage = 'VLAN successfully set'
                    result.errorMessage = ''
                    result.success = True
                    result.updatedInterface = connection_result.mac_address
                    results.append(result)

            except Exception as ex:
                error_result = self._create_failure_result(action, ex)
                results.append(error_result)

        return results

    @staticmethod
    def _get_error_message_from_exception(ex):
        error_message = ''
        if hasattr(ex, 'msg'):
            error_message = ex.msg
        if hasattr(ex, 'faultMessage'):
            if hasattr(ex.faultMessage, 'message'):
                error_message += '. ' + ex.faultMessage.message
        return error_message

    def _remove_vlan_bulk(self, action, default_network, vm_uuid, connection_details):
        mappings = []
        results = []
        interface_attributes = [attr.attributeValue for attr in action.connectorAttributes
                                if attr.attributeName == 'Interface']

        for interface_attribute in interface_attributes:
            vm_network_remove_mapping = VmNetworkRemoveMapping()
            vm_network_remove_mapping.mac_address = interface_attribute
            vm_network_remove_mapping.vm_uuid = vm_uuid
            mappings.append(vm_network_remove_mapping)

        if not mappings:
            error_result = ActionResult()
            error_result.actionId = str(action.actionId)
            error_result.type = str(action.type)
            error_result.infoMessage = str('')
            error_result.errorMessage = 'Interface attribute is missing on connectorAttributes for removeVlan action'
            error_result.success = False
            error_result.updatedInterface = None
            results = [error_result]
        else:
            try:
                connection_results = self.command_wrapper.execute_command_with_connection(
                    connection_details,
                    self.virtual_switch_disconnect_command.disconnect_from_networks,
                    vm_uuid,
                    mappings)

                for connection_result in connection_results:
                    result = self._create_successful_result(action, connection_result)
                    results.append(result)

            except Exception as ex:
                error_result = self._create_failure_result(action, ex)
                results.append(error_result)

        return results

    @staticmethod
    def _create_successful_result(action, connection_result):
        result = ActionResult()
        result.actionId = str(action.actionId)
        result.type = str(action.type)
        result.infoMessage = 'VLAN successfully set'
        result.errorMessage = ''
        result.success = True
        result.updatedInterface = connection_result.vnic.macAddress
        return result

    @staticmethod
    def _create_failure_result(action, ex):
        error_result = ActionResult()
        error_result.actionId = str(action.actionId)
        error_result.type = str(action.type)
        error_result.infoMessage = str('')
        error_result.errorMessage = CommandOrchestrator._get_error_message_from_exception(ex)
        error_result.success = False
        error_result.updatedInterface = None
        return error_result
