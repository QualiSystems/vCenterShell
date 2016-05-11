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
        """

        :param connector:
        :type connector: cloudshell.cp.vcenter.commands.connect_dvswitch.VirtualSwitchConnectCommand
        :param disconnector:
        :type disconnector: cloudshell.cp.vcenter.commands.disconnect_dvswitch.VirtualSwitchToMachineDisconnectCommand
        :param resource_model_parser:
        :return:
        """
        self.connector = connector
        self.disconnector = disconnector
        self.resource_model_parser = resource_model_parser
        self.vcenter_data_model = None
        self.reserved_networks = []
        self.dv_switch_path = ''
        self.dv_switch_name = ''
        self.default_network = ''
        self.logger = None

    def connect_bulk(self, si, logger, vcenter_data_model, request):
        """
        :param si:
        :param logger:
        :param VMwarevCenterResourceModel vcenter_data_model:
        :param request:
        :return:
        """
        self.logger = logger

        self.logger.info('Apply connectivity changes has started')
        self.logger.debug('Apply connectivity changes has started with the requet: {0}'.format(request))

        holder = DeployDataHolder(jsonpickle.decode(request))

        self.vcenter_data_model = vcenter_data_model
        if vcenter_data_model.reserved_networks:
            self.reserved_networks = [name.strip() for name in vcenter_data_model.reserved_networks.split(',')]

        if not vcenter_data_model.default_dvswitch:
            return self._handle_no_dvswitch_error(holder)

        dvswitch_location = VMLocation.create_from_full_path(vcenter_data_model.default_dvswitch)

        self.dv_switch_path = VMLocation.combine([vcenter_data_model.default_datacenter, dvswitch_location.path])
        self.dv_switch_name = dvswitch_location.name
        self.default_network = VMLocation.combine(
            [vcenter_data_model.default_datacenter, vcenter_data_model.holding_network])

        mappings = self._map_requsets(holder.driverRequest.actions)
        self.logger.debug('Connectivity actions mappings: {0}'.format(jsonpickle.encode(mappings, unpicklable=False)))

        pool = ThreadPool()
        async_results = self._run_async_connection_actions(si, mappings, pool, logger)

        results = self._get_async_results(async_results, pool)
        self.logger.info('Apply connectivity changes done')
        self.logger.debug('Apply connectivity has finished with the results: {0}'.format(jsonpickle.encode(results,
                                                                                                           unpicklable=False)))
        return results

    def _handle_no_dvswitch_error(self, holder):
        error = ValueError('Please set the attribute "Default DvSwitch" in order to execute any connectivity changes')
        err_res = []
        for action in holder.driverRequest.actions:
            err_res.append(self._create_error_action_res(action, error))
        return err_res

    def _map_requsets(self, actions):
        grouped_by_vm_by_requset_by_mode = self._group_action(actions)
        vm_mapping = self._create_mapping_from_groupings(grouped_by_vm_by_requset_by_mode)
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

    def _create_mapping_from_groupings(self, grouped_by_vm_by_requset_by_mode):
        vm_mapping = dict()
        for vm, req_to_modes in grouped_by_vm_by_requset_by_mode.items():
            actions_mapping = self.ActionsMapping()

            remove_mappings = self._get_remove_mappings(req_to_modes, vm)
            actions_mapping.remove_mapping = remove_mappings

            set_mappings = self._get_set_mappings(req_to_modes)
            actions_mapping.set_mapping = set_mappings

            actions_mapping.action_tree = req_to_modes
            vm_mapping[vm] = actions_mapping

        return vm_mapping

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
        vnic_to_network.vlan_id = vlan_id
        vnic_to_network.vlan_spec = mode
        return vnic_to_network

    def _run_async_connection_actions(self, si, mappings, pool, logger):

        async_results = []
        for vm, action_mappings in mappings.items():
            async_results.append(pool.apply_async(self._apply_connectivity_changes, (si, vm, action_mappings, logger)))
        return async_results

    def _apply_connectivity_changes(self, si, vm_uuid, action_mappings, logger):
        results = []
        if action_mappings.remove_mapping:
            remove_results = self._remove_vlan(action_mappings, si, vm_uuid, logger)
            results += remove_results

        if action_mappings.set_mapping:
            set_results = self._set_vlan(action_mappings, si, vm_uuid, logger)
            results += set_results
        return results

    def _set_vlan(self, action_mappings, si, vm_uuid, logger):
        results = []
        set_vlan_actions = action_mappings.action_tree[ACTION_TYPE_SET_VLAN]
        try:
            self.logger.info('connecting vm({0})'.format(vm_uuid))
            self.logger.debug('connecting vm({0}) with the mappings'.format(vm_uuid,
                                                                            jsonpickle.encode(action_mappings,
                                                                                              unpicklable=False)))
            connection_results = self.connector.connect_to_networks(si=si,
                                                                    logger=logger,
                                                                    vm_uuid=vm_uuid,
                                                                    vm_network_mappings=action_mappings.set_mapping,
                                                                    default_network_name=self.default_network,
                                                                    reserved_networks=self.reserved_networks,
                                                                    dv_switch_name=self.dv_switch_name)

            connection_res_map = self._prepare_connection_results_for_extraction(connection_results)
            act_by_mode_by_vlan = self._group_action_by_vlan_id(set_vlan_actions)
            act_by_mode_by_vlan_by_nic = self._group_actions_by_vlan_by_vnic(act_by_mode_by_vlan)
            results += self._get_set_vlan_result_suc(act_by_mode_by_vlan_by_nic, connection_res_map)

        except Exception as e:
            self.logger.error('Exception raised while connecting vm({0}) with exception: {1}'.format(vm_uuid, e))
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

    def _remove_vlan(self, action_mappings, si, vm_uuid, logger):

        results = []
        mode_to_actions = action_mappings.action_tree[ACTION_TYPE_REMOVE_VLAN]
        try:
            self.logger.info('disconnecting vm({0})'.format(vm_uuid))
            self.logger.debug('disconnecting vm({0}) with the mappings'.format(vm_uuid,
                                                                               jsonpickle.encode(action_mappings,
                                                                                                 unpicklable=False)))
            connection_results = self.disconnector.disconnect_from_networks(si,
                                                                            logger,
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
            self.logger.error('Exception raised while disconnecting vm({0}) with exception: {1}'.format(vm_uuid, e))
            for mode, actions in mode_to_actions.items():
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
        error_result.updatedInterface = ConnectionCommandOrchestrator._get_mac(action)
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
