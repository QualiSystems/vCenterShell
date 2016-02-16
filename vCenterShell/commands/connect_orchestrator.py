import copy
import uuid
from multiprocessing.pool import ThreadPool

import jsonpickle

from common.utilites.command_result import set_command_result
from models.ActionResult import ActionResult
from models.DeployDataHolder import DeployDataHolder
from models.DriverResponse import DriverResponse, DriverResponseRoot
from vCenterShell.commands.combine_action import CombineAction
from vCenterShell.vm.dvswitch_connector import VmNetworkMapping, VmNetworkRemoveMapping


class ConnectionCommandOrchestrator(object):
    def __init__(self, vc_data_model, connections_commands):
        self.connections_commands = connections_commands
        self.vc_data_model = vc_data_model

    def connect_bulk(self, si, request):
        dv_switch_path = self.vc_data_model.default_dvswitch_path
        dv_switch_name = self.vc_data_model.default_dvswitch_name
        port_group_path = self.vc_data_model.default_port_group_path
        default_network = self.vc_data_model.default_network
        holder = DeployDataHolder(jsonpickle.decode(request))

        mappings = self._group_actions_by_uuid_and_mode(holder.driverRequest.actions)
        unified_actions = self._create_new_action_by_mapping(mappings)

        async_results = self.run_async_connection_actions(default_network, dv_switch_name, dv_switch_path,
                                                          port_group_path, si, unified_actions)

        return self._get_async_results(async_results, unified_actions)

    def run_async_connection_actions(self, default_network, dv_switch_name, dv_switch_path, port_group_path, si,
                                     unified_actions):
        async_results = []
        pool = ThreadPool()
        for action in unified_actions:
            vm_uuid = self._get_vm_uuid(action)
            if action.type == 'setVlan':
                res = pool.apply_async(self._set_vlan_bulk,
                                       (action, default_network, dv_switch_name, dv_switch_path,
                                        port_group_path,
                                        vm_uuid, si))

            elif action.type == 'removeVlan':

                res = pool.apply_async(self._remove_vlan_bulk,
                                       (action, default_network, vm_uuid, si))

            if res:
                async_results.append(res)
        return async_results

    def _set_vlan_bulk(self, action, default_network, dv_switch_name, dv_switch_path, port_group_path, vm_uuid, si):

        mappings = self._create_connect_mappings(action, dv_switch_name, dv_switch_path, port_group_path)

        results = []
        if mappings:
            try:
                connection_results = self.connections_commands.connect_to_networks(si, vm_uuid, mappings,
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

    def _remove_vlan_bulk(self, action, vm_uuid, si):
        mappings = self._create_disconnection_mappings(action, vm_uuid)

        results = []
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
                connection_results = self.connections_commands.disconnect_from_networks(si, vm_uuid, mappings)

                for connection_result in connection_results:
                    result = self._create_successful_result(action, connection_result)
                    results.append(result)

            except Exception as ex:
                error_result = self._create_failure_result(action, ex)
                results.append(error_result)

        return results

    @staticmethod
    def _create_disconnection_mappings(action, vm_uuid):
        mappings = []
        interface_attributes = [attr.attributeValue for attr in action.connectorAttributes
                                if attr.attributeName == 'Interface']
        for interface_attribute in interface_attributes:
            vm_network_remove_mapping = VmNetworkRemoveMapping()
            vm_network_remove_mapping.mac_address = interface_attribute
            vm_network_remove_mapping.vm_uuid = vm_uuid
            mappings.append(vm_network_remove_mapping)
        return mappings

    @staticmethod
    def _group_actions_by_uuid_and_mode(actions):
        key_to_actions = dict()

        # group by machine and vlan mode and action type
        for action in actions:
            vm_uuid = ConnectionCommandOrchestrator._get_vm_uuid(action)
            vlan_mode = action.connectionParams.mode
            action_type = action.type
            key = (vm_uuid, vlan_mode, action_type)
            if key not in key_to_actions:
                key_to_actions[key] = []
            key_to_actions[key].append(action)

        # generate new keys
        return {uuid.uuid4(): action
                for key, action in key_to_actions.items()}

    @staticmethod
    def _create_new_action_by_mapping(mapping):
        actions = []

        for key, actions_arr in mapping.items():
            action = copy.deepcopy(actions_arr[0])
            action.actionId = key
            for act in actions_arr[1:]:
                CombineAction.combine(action, act)
            actions.append(action)
        return actions

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
        error_result.errorMessage = ConnectionCommandOrchestrator._get_error_message_from_exception(ex)
        error_result.success = False
        error_result.updatedInterface = None
        return error_result

    @staticmethod
    def _get_error_message_from_exception(ex):
        error_message = ''
        if hasattr(ex, 'msg'):
            error_message = ex.msg
        if hasattr(ex, 'faultMessage'):
            if hasattr(ex.faultMessage, 'message'):
                error_message += '. ' + ex.faultMessage.message
        return error_message

    @staticmethod
    def _get_vm_uuid(action):
        vm_uuid_values = [attr.attributeValue for attr in action.customActionAttributes
                          if attr.attributeName == 'VM_UUID']

        if vm_uuid_values and vm_uuid_values[0]:
            return vm_uuid_values[0]

        raise ValueError('VM_UUID is missing on action attributes')

    @staticmethod
    def _get_vnic_name(action):
        vnic_name_values = [attr.attributeValue for attr in action.customActionAttributes
                            if attr.attributeName == 'Vnic Name']
        if vnic_name_values:
            return vnic_name_values[0]
        return None

    @staticmethod
    def _get_async_results(async_results, unified_actions):
        results = []
        for async_result in async_results:
            action_results = async_result.get()
            for action_result in action_results:
                for unified_action in unified_actions[action_result.actionId]:
                    copied_action = copy.deepcopy(action_result)
                    copied_action.actionId = unified_action.actionId
                    results.append(copied_action)
        return results

    @staticmethod
    def _create_connect_mappings(action, dv_switch_name, dv_switch_path, port_group_path):
        mappings = []
        for vlan in action.connectionParams.vlanIds:
            vnic_to_network = VmNetworkMapping()
            vnic_to_network.dv_switch_path = dv_switch_path
            vnic_to_network.dv_switch_name = dv_switch_name
            vnic_to_network.port_group_path = port_group_path
            vnic_to_network.vlan_id = vlan
            vnic_to_network.vlan_spec = action.connectionParams.mode

            vnic_name = ConnectionCommandOrchestrator._get_vnic_name(action)
            if vnic_name:
                vnic_to_network.vnic_name = vnic_name

            mappings.append(vnic_to_network)
        return mappings
