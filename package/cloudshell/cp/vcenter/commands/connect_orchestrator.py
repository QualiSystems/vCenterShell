import copy
import traceback
import uuid
from multiprocessing.pool import ThreadPool

import jsonpickle
from cloudshell.cp.vcenter.commands.combine_action import CombineAction
from cloudshell.cp.vcenter.models.ActionResult import CustomActionResult
from cloudshell.cp.vcenter.models.DeployDataHolder import DeployDataHolder
from cloudshell.cp.vcenter.vm.dvswitch_connector import VmNetworkMapping, VmNetworkRemoveMapping
from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from cloudshell.cp.vcenter.common.utilites.common_utils import get_error_message_from_exception


class ConnectionCommandOrchestrator(object):
    def __init__(self, connector, disconnector, resource_model_parser):
        self.connector = connector
        self.disconnector = disconnector
        self.resource_model_parser = resource_model_parser

    def connect_bulk(self, si, vcenter_data_model, request):
        """
        :param si:
        :param VMwarevCenterResourceModel vcenter_data_model:
        :param request:
        :return:
        """
        self.reserved_networks = []
        self.vcenter_data_model = vcenter_data_model
        if vcenter_data_model.reserved_networks:
            self.reserved_networks = [name.strip() for name in vcenter_data_model.reserved_networks.split(',')]

        dvswitch_location = VMLocation.create_from_full_path(vcenter_data_model.default_dvswitch)

        self.dv_switch_path = VMLocation.combine([vcenter_data_model.default_datacenter, dvswitch_location.path])
        self.dv_switch_name = dvswitch_location.name
        self.port_group_path = vcenter_data_model.default_port_group_location
        self.default_network = VMLocation.combine(
            [vcenter_data_model.default_datacenter, vcenter_data_model.holding_network])
        holder = DeployDataHolder(jsonpickle.decode(request))

        mappings = self._map_requsets(holder.driverRequest.actions)

        pool = ThreadPool()
        async_results = self._run_async_connection_actions(si, mappings, pool)

        results = self._get_async_results(async_results, mappings, pool)

        return results

    class ActionsMapping(object):
        def __init__(self):
            self.action_tree = ''
            self.remove_mapping = ''
            self.set_mapping = ''

    def _map_requsets(self, actions):
        grouped_by_vm = dict()
        grouped_by_vm_by_requset = dict()
        grouped_by_vm_by_requset_by_mode = dict()
        vm_mapping = dict()

        for action in actions:
            vm_uuid = ConnectionCommandOrchestrator._get_vm_uuid(action)
            self._add_safely_to_dict(value=action, dictionary=grouped_by_vm, key=vm_uuid)

        for machine, actions in grouped_by_vm.items():
            grouped_by_vm_by_requset[machine] = dict()
            for action in actions:
                self._add_safely_to_dict(key=action.type, dictionary=grouped_by_vm_by_requset[machine], value=action)

        for machine, req_to_actions in grouped_by_vm_by_requset.items():
            grouped_by_vm_by_requset_by_mode[machine] = dict()
            for req_type, actions in req_to_actions.items():
                grouped_by_vm_by_requset_by_mode[machine][req_type] = dict()
                for action in actions:
                    self._add_safely_to_dict(value=action,
                                             dictionary=grouped_by_vm_by_requset_by_mode[machine][req_type],
                                             key=action.connectionParams.mode)

        self._create_mapping_from_groupings(grouped_by_vm_by_requset_by_mode, vm_mapping)
        return vm_mapping

    def _create_mapping_from_groupings(self, grouped_by_vm_by_requset_by_mode, vm_mapping):
        for vm, req_to_modes in grouped_by_vm_by_requset_by_mode.items():
            actions_mapping = self.ActionsMapping()

            remove_mappings = self._get_remove_mappings(req_to_modes, vm)
            actions_mapping.remove_mapping = remove_mappings

            set_mappings = self._get_set_mappings(req_to_modes)
            actions_mapping.set_mapping = set_mappings

            actions_mapping.action_tree = req_to_modes
            vm_mapping[vm] = actions_mapping

    def _get_remove_mappings(self, req_to_modes, vm):
        remove_mappings = []
        if 'removeVlan' in req_to_modes:
            remove_requests = [actions for mode, actions in req_to_modes['removeVlan'].items()][0]
            for action in remove_requests:
                interface_attributes = \
                    [attr.attributeValue for attr in action.connectorAttributes
                     if attr.attributeName == 'Interface']
                for interface_attribute in interface_attributes:
                    vm_network_remove_mapping = VmNetworkRemoveMapping()
                    vm_network_remove_mapping.mac_address = interface_attribute
                    vm_network_remove_mapping.vm_uuid = vm
                    remove_mappings.append(vm_network_remove_mapping)
        return remove_mappings

    def _get_set_mappings(self, req_to_modes):
        set_mappings = []
        if 'setVlan' in req_to_modes:
            set_requests = req_to_modes['setVlan']
            for mode, actions in set_requests.items():
                for action in actions:
                    vnic_name = ConnectionCommandOrchestrator._get_vnic_name(action)
                    if vnic_name:
                        vnic_to_network = self._create_map(action.connectionParams.vlanIds[0], mode, vnic_name)
                        set_mappings.append(vnic_to_network)
                    else:
                        for vlan in action.connectionParams.vlanIds:
                            vnic_to_network = self._create_map(vlan, mode)
                            set_mappings.append(vnic_to_network)

        # this line makes sure that the vNICS with names are first
        return sorted(set_mappings, key=lambda x: x.vnic_name, reverse=True)

    def _create_map(self, vlan_id, mode, vnic_name=None):
        vnic_to_network = VmNetworkMapping()
        vnic_to_network.vnic_name = vnic_name
        vnic_to_network = VmNetworkMapping()
        vnic_to_network.dv_switch_path = self.dv_switch_path
        vnic_to_network.dv_switch_name = self.dv_switch_name
        vnic_to_network.port_group_path = self.port_group_path
        vnic_to_network.vlan_id = vlan_id
        vnic_to_network.vlan_spec = mode
        return vnic_to_network

    def _run_async_connection_actions(self, si, mappings, pool):

        async_results = []
        for vm, action_mappings in mappings.items():
            async_results.append(pool.apply_async(self._apply_connectivity_changes, (si, vm, action_mappings)))
        return async_results

    def _apply_connectivity_changes(self, si, vm_uuid, action_mappings):
        if action_mappings.remove_mapping:
            connection_results = self.disconnector.disconnect_from_networks(si,
                                                                            self.vcenter_data_model,
                                                                            vm_uuid,
                                                                            action_mappings.remove_mapping)
        if action_mappings.set_mapping:
            connection_results = self.connector.connect_to_networks(si,
                                                                    vm_uuid,
                                                                    action_mappings.set_mapping,
                                                                    self.default_network,
                                                                    self.reserved_networks)
        return connection_results

    def _set_vlan_bulk(self, actions, default_network, dv_switch_name, dv_switch_path, port_group_path, vm_uuid,
                       reserved_networks, si):
        results = []
        for action in actions:
            mappings = self._create_connect_mappings(action, dv_switch_name, dv_switch_path, port_group_path)

            if mappings:
                try:
                    connection_results = self.connector.connect_to_networks(si, vm_uuid, mappings,
                                                                            default_network, reserved_networks)
                    for connection_result in connection_results:
                        result = CustomActionResult()
                        result.actionId = str(action.actionId)
                        result.type = str(action.type)
                        result.infoMessage = 'VLAN successfully set'
                        result.errorMessage = ''
                        result.success = True
                        result.updatedInterface = connection_result.mac_address
                        result.network_name = connection_result.network_name
                        results.append(result)

                except Exception as ex:
                    # todo: write exception stacktrace to log
                    error_result = self._create_failure_result(action, ex)
                    results.append(error_result)

        return results

    def _remove_vlan_bulk(self, action, vm_uuid, si, vcenter_data_model):
        mappings = self._create_disconnection_mappings(action, vm_uuid)

        results = []
        if not mappings:
            error_result = CustomActionResult()
            error_result.actionId = str(action.actionId)
            error_result.type = str(action.type)
            error_result.infoMessage = str('')
            error_result.errorMessage = 'Interface attribute is missing on connectorAttributes for removeVlan action'
            error_result.success = False
            error_result.updatedInterface = None
            results = [error_result]
        else:
            try:
                connection_results = self.disconnector.disconnect_from_networks(si, vcenter_data_model,
                                                                                vm_uuid, mappings)

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
            # vlan_mode = action.connectionParams.mode
            action_type = action.type
            key = (vm_uuid,
                   # vlan_mode,
                   action_type)
            ConnectionCommandOrchestrator._add_safely_to_dict(action, key_to_actions, key)

        # generate new keys
        return {str(uuid.uuid4()): action
                for key, action in key_to_actions.items()}

    @staticmethod
    def _create_new_action_by_mapping(mapping):
        actions = dict()

        for key, actions_arr in mapping.items():
            actions_by_modes = dict()
            for action in actions_arr:
                ConnectionCommandOrchestrator._add_safely_to_dict(action, actions_by_modes,
                                                                  action.connectionParams.mode)

            for mode, actions_by_mode_arr in actions_by_modes.items():
                act = copy.deepcopy(actions_by_mode_arr[0])
                act.actionId = key

                if not ConnectionCommandOrchestrator._have_vnic_request(act):
                    for act_to_combine in actions_by_mode_arr[1:]:
                        if not ConnectionCommandOrchestrator._have_vnic_request(act_to_combine):
                            CombineAction.combine(act, act_to_combine)
                        else:
                            s_act = copy.deepcopy(act_to_combine)
                            s_act.actionId = key
                            ConnectionCommandOrchestrator._add_safely_to_dict(s_act, actions, key)
                    ConnectionCommandOrchestrator._add_safely_to_dict(act, actions, key)
                else:
                    # if one of them have a requested vnic it wont combine
                    ConnectionCommandOrchestrator._add_safely_to_dict(act, actions, key)
                    for act_to_combine in actions_by_mode_arr[1:]:
                        s_act = copy.deepcopy(act_to_combine)
                        s_act.actionId = key
                        ConnectionCommandOrchestrator._add_safely_to_dict(s_act, actions, key)

        return actions

    @staticmethod
    def _add_safely_to_dict(value, dictionary, key):
        if key not in dictionary:
            dictionary[key] = []
        dictionary[key].append(value)

    @staticmethod
    def _have_vnic_request(action):
        if not [att for att in action.customActionAttributes if att.attributeName == 'Vnic Name']:
            return False
        return True

    @staticmethod
    def _create_successful_result(action, connection_result):
        result = CustomActionResult()
        result.actionId = str(action.actionId)
        result.type = str(action.type)
        result.infoMessage = 'VLAN successfully set'
        result.errorMessage = ''
        result.success = True
        result.updatedInterface = connection_result.vnic_mac
        return result

    @staticmethod
    def _create_failure_result(action, ex):
        error_result = CustomActionResult()
        error_result.actionId = str(action.actionId)
        error_result.type = str(action.type)
        error_result.infoMessage = str('')
        error_result.errorMessage = get_error_message_from_exception(ex)
        error_result.success = False
        error_result.updatedInterface = None
        return error_result

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
    def _get_async_results(async_results, unified_actions, pool):
        pool.close()
        pool.join()
        results = []
        for async_result in async_results:
            action_results = async_result.get()
            for action_result in action_results:
                if action_result.success:
                    res = ConnectionCommandOrchestrator._decombine_success_action_result(action_result,
                                                                                         unified_actions, results)
                    for i in range(0, len(unified_actions[action_result.actionId])):
                        action = unified_actions[action_result.actionId][i]
                        if action.actionId == res.actionId:
                            unified_actions[action_result.actionId].remove(action)
                            break
                else:
                    ConnectionCommandOrchestrator._decombine_failed_action_result(action_result,
                                                                                  unified_actions, results)
        return results

    @staticmethod
    def _decombine_failed_action_result(action_result, unified_actions, results):
        for unified_action in unified_actions[action_result.actionId]:
            result = ConnectionCommandOrchestrator._decombine(unified_action, action_result)
            if result:
                results.append(result)

    @staticmethod
    def _decombine_success_action_result(action_result, unified_actions, results):
        for unified_action in unified_actions[action_result.actionId]:
            result = ConnectionCommandOrchestrator._decombine(unified_action, action_result)
            if result:
                results.append(result)
                return result

    @staticmethod
    def _decombine_setVlan(unified_action, action_result):
        name = str(action_result.network_name)
        for vlan_id in unified_action.connectionParams.vlanIds:
            sub = '_{0}_'.format(str(vlan_id))
            if name.find(sub) > -1 or not action_result.success:
                copied_action = action_result.get_base_class()
                copied_action.actionId = unified_action.actionId
                return copied_action
        return None

    @staticmethod
    def _decombine_removeVlan(unified_action, action_result):
        """
            :type action_result: CustomActionResult
        """
        mac = str(action_result.updatedInterface)
        interfaces = [inter
                      for inter in unified_action.connectorAttributes
                      if inter.attributeName == "Interface"]
        for interface in interfaces:
            if not action_result.success or mac == str(interface.attributeValue):
                copied_action = action_result.get_base_class()
                copied_action.actionId = unified_action.actionId
                return copied_action
        return None

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

    @classmethod
    def _decombine(self, unified_action, action_result):
        method_name = '_decombine_' + unified_action.type

        if not hasattr(self, method_name):
            raise ValueError('Action type {0} is not supported'.format(unified_action.type))

        method = getattr(self, method_name)
        return method(unified_action, action_result)
