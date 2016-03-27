from multiprocessing.pool import ThreadPool

import jsonpickle
from cloudshell.cp.vcenter.models.ActionResult import ActionResult
from cloudshell.cp.vcenter.models.DeployDataHolder import DeployDataHolder
from cloudshell.cp.vcenter.vm.dvswitch_connector import VmNetworkMapping, VmNetworkRemoveMapping
from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from cloudshell.cp.vcenter.common.utilites.common_utils import get_error_message_from_exception

SUCCESSFULLY_REMOVED = 'VLAN Successfully removed'
ACTION_TYPE_SET_VLAN = 'setVlan'
ACTION_SUCCESS_MSG = 'VLAN successfully set'
INTERFACE = 'Interface'
ACTION_TYPE_REMOVE_VLAN = 'removeVlan'


class ConnectionCommandOrchestrator(object):
    def __init__(self, connector, disconnector, resource_model_parser):
        self.connector = connector
        self.disconnector = disconnector
        self.resource_model_parser = resource_model_parser
        self.vcenter_data_model = None
        self.reserved_networks = []
        self.dv_switch_path = ''
        self.dv_switch_name = ''
        self.port_group_path = ''
        self.default_network = ''

    def connect_bulk(self, si, vcenter_data_model, request):
        """
        :param si:
        :param VMwarevCenterResourceModel vcenter_data_model:
        :param request:
        :return:
        """
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

        results = self._get_async_results(async_results, pool)

        return results

    def _map_requsets(self, actions):
        vm_mapping = dict()

        grouped_by_vm_by_requset_by_mode = self._group_action(actions)
        self._create_mapping_from_groupings(grouped_by_vm_by_requset_by_mode, vm_mapping)

        return vm_mapping

    def _group_action(self, actions):
        grouped_by_vm = self._group_action_by_vm(actions)
        grouped_by_vm_by_requset = self._group_vm_actions_by_req_type(grouped_by_vm)
        grouped_by_vm_by_requset_by_mode = self._group_vm_action_type_by_mode(grouped_by_vm_by_requset)
        return grouped_by_vm_by_requset_by_mode

    def _group_vm_action_type_by_mode(self, grouped_by_vm_by_requset):
        grouped_by_vm_by_requset_by_mode = dict()
        for machine, req_to_actions in grouped_by_vm_by_requset.items():
            grouped_by_vm_by_requset_by_mode[machine] = dict()
            for req_type, actions in req_to_actions.items():
                grouped_by_vm_by_requset_by_mode[machine][req_type] = dict()
                for action in actions:
                    self._add_safely_to_dict(dictionary=grouped_by_vm_by_requset_by_mode[machine][req_type],
                                             key=action.connectionParams.mode,
                                             value=action)
        return grouped_by_vm_by_requset_by_mode

    def _group_vm_actions_by_req_type(self, grouped_by_vm):
        grouped_by_vm_by_requset = dict()
        for machine, actions in grouped_by_vm.items():
            grouped_by_vm_by_requset[machine] = dict()
            for action in actions:
                self._add_safely_to_dict(dictionary=grouped_by_vm_by_requset[machine], key=action.type, value=action)
        return grouped_by_vm_by_requset

    def _group_action_by_vm(self, actions):
        grouped_by_vm = dict()
        for action in actions:
            vm_uuid = ConnectionCommandOrchestrator._get_vm_uuid(action)
            self._add_safely_to_dict(dictionary=grouped_by_vm, key=vm_uuid, value=action)
        return grouped_by_vm

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
        if ACTION_TYPE_REMOVE_VLAN in req_to_modes:
            for mode, actions in req_to_modes[ACTION_TYPE_REMOVE_VLAN].items():
                for action in actions:
                    interface_attributes = \
                        [attr.attributeValue for attr in action.connectorAttributes
                         if attr.attributeName == INTERFACE]
                    for interface_attribute in interface_attributes:
                        vm_network_remove_mapping = VmNetworkRemoveMapping()
                        vm_network_remove_mapping.mac_address = interface_attribute
                        vm_network_remove_mapping.vm_uuid = vm
                        remove_mappings.append(vm_network_remove_mapping)
        return remove_mappings

    def _get_set_mappings(self, req_to_modes):
        set_mappings = []
        if ACTION_TYPE_SET_VLAN in req_to_modes:
            set_requests = req_to_modes[ACTION_TYPE_SET_VLAN]
            for mode, actions in set_requests.items():
                for action in actions:
                    vnic_name = self._get_vnic_name(action)
                    vnic_to_network = self._create_map(action.connectionParams.vlanId, mode, vnic_name)
                    set_mappings.append(vnic_to_network)

        # this line makes sure that the vNICS with names are first
        return sorted(set_mappings, key=lambda x: x.vnic_name, reverse=True)

    def _create_map(self, vlan_id, mode, vnic_name):
        vnic_to_network = VmNetworkMapping()
        vnic_to_network.vnic_name = self._validate_vnic_name(vnic_name)
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
        results = []
        if action_mappings.remove_mapping:
            remove_results = self._remove_vlan(action_mappings, si, vm_uuid)
            results += remove_results

        if action_mappings.set_mapping:
            set_results = self._set_vlan(action_mappings, si, vm_uuid)
            results += set_results
        return results

    def _set_vlan(self, action_mappings, si, vm_uuid):
        results = []
        set_vlan_actions = action_mappings.action_tree[ACTION_TYPE_SET_VLAN]
        try:
            connection_results = self.connector.connect_to_networks(si,
                                                                    vm_uuid,
                                                                    action_mappings.set_mapping,
                                                                    self.default_network,
                                                                    self.reserved_networks)

            connection_res_map = self._prepare_connection_results_for_extraction(connection_results)
            act_by_mode_by_vlan = self._group_action_by_vlan_id(set_vlan_actions)
            act_by_mode_by_vlan_by_nic = self._group_actions_by_vlan_by_vnic(act_by_mode_by_vlan)
            results += self._get_set_vlan_result_suc(act_by_mode_by_vlan_by_nic, connection_res_map)

        except Exception as e:
            for mode, actions in set_vlan_actions.items():
                for action in actions:
                    error_result = self._create_error_action_res(action, e)
                    results.append(error_result)

        return results

    def _prepare_connection_results_for_extraction(self, connection_results):
        connection_res_map = dict()
        for connection_result in connection_results:
            vlan_spec = connection_result.network_name.split('_')
            mode = vlan_spec[len(vlan_spec) - 1]
            id = vlan_spec[len(vlan_spec) - 2]
            if mode not in connection_res_map:
                connection_res_map[mode] = dict()
            if id not in connection_res_map[mode]:
                connection_res_map[mode][id] = dict()

            self._add_safely_to_dict(dictionary=connection_res_map[mode][id],
                                     key=connection_result.requested_vnic,
                                     value=connection_result)
        return connection_res_map

    def _get_set_vlan_result_suc(self, act_by_mode_by_vlan_by_nic, connection_res_map):
        results = []
        for mode, vlans_to_nics in act_by_mode_by_vlan_by_nic.items():
            for vlan_id, nics_to_actions in vlans_to_nics.items():
                for nic_name, actions in nics_to_actions.items():
                    nic_name = self._validate_vnic_name(nic_name)
                    for action in actions:
                        res = connection_res_map[mode][vlan_id][nic_name][0]
                        connection_res_map[mode][vlan_id][nic_name].remove(res)
                        result = ActionResult()
                        result.actionId = action.actionId
                        result.success = True
                        result.errorMessage = None
                        result.infoMessage = ACTION_SUCCESS_MSG
                        result.type = ACTION_TYPE_SET_VLAN
                        result.updatedInterface = res.mac_address
                        results.append(result)
        return results

    def _group_actions_by_vlan_by_vnic(self, set_actions_grouped_by_vlan_id):
        set_act_group_by_mode_by_vlan_by_requsted_vnic = dict()
        for mode, vlan_to_action in set_actions_grouped_by_vlan_id.items():
            set_act_group_by_mode_by_vlan_by_requsted_vnic[mode] = dict()
            for vlan_id, actions in vlan_to_action.items():
                set_act_group_by_mode_by_vlan_by_requsted_vnic[mode][vlan_id] = dict()
                for action in actions:
                    name = self._get_vnic_name(action)
                    self._add_safely_to_dict(
                        dictionary=set_act_group_by_mode_by_vlan_by_requsted_vnic[mode][vlan_id],
                        key=name,
                        value=action)
        return set_act_group_by_mode_by_vlan_by_requsted_vnic

    def _group_action_by_vlan_id(self, set_vlan_actions):
        set_actions_grouped_by_vlan_id = dict()
        for mode, actions in set_vlan_actions.items():
            set_actions_grouped_by_vlan_id[mode] = dict()
            for action in actions:
                vlan_id = action.connectionParams.vlanId
                self._add_safely_to_dict(dictionary=set_actions_grouped_by_vlan_id[mode], key=vlan_id, value=action)
        return set_actions_grouped_by_vlan_id

    def _remove_vlan(self, action_mappings, si, vm_uuid):
        results = []
        mode_to_actions = action_mappings.action_tree[ACTION_TYPE_REMOVE_VLAN]
        try:
            connection_results = self.disconnector.disconnect_from_networks(si,
                                                                            self.vcenter_data_model,
                                                                            vm_uuid,
                                                                            action_mappings.remove_mapping)

            interface_to_action = dict()
            for mode, actions in mode_to_actions.items():
                for action in actions:
                    name = self._get_mac(action)
                    interface_to_action[name] = action

            for res in connection_results:
                action = interface_to_action[res.vnic_mac]
                action_result = ActionResult()
                action_result.actionId = action.actionId
                action_result.success = True
                action_result.infoMessage = SUCCESSFULLY_REMOVED
                action_result.type = ACTION_TYPE_REMOVE_VLAN
                action_result.errorMessage = None
                action_result.updatedInterface = res.vnic_mac
                results.append(action_result)
        except Exception as e:
            for mode, actions in mode_to_actions:
                for action in actions:
                    error_result = self._create_error_action_res(action, e)
                    results.append(error_result)
        return results

    @staticmethod
    def _create_error_action_res(action, e):
        error_result = ActionResult()
        error_result.actionId = action.actionId
        error_result.type = action.type
        error_result.errorMessage = get_error_message_from_exception(e)
        error_result.infoMessage = None
        error_result.success = False
        return error_result

    @staticmethod
    def _add_safely_to_dict(value, dictionary, key):
        if key not in dictionary:
            dictionary[key] = []
        dictionary[key].append(value)

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
    def _get_async_results(async_results, pool):
        pool.close()
        pool.join()
        results = []
        for async_result in async_results:
            action_results = async_result.get()
            results += action_results
        return results

    @staticmethod
    def _get_mac(action):
        for att in action.connectorAttributes:
            if att.attributeName == INTERFACE:
                return att.attributeValue
        return None

    class ActionsMapping(object):
        def __init__(self):
            self.action_tree = ''
            self.remove_mapping = ''
            self.set_mapping = ''

    @staticmethod
    def _validate_vnic_name(vnic_name):
        if not vnic_name:
            return None

        if str(vnic_name).isdigit():
            vnic_name = 'Network adapter {0}'.format(vnic_name)
        return vnic_name
