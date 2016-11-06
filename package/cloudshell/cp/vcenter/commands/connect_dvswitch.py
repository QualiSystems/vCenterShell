from cloudshell.cp.vcenter.models.ConnectionResult import ConnectionResult


class VirtualSwitchConnectCommand:
    def __init__(self,
                 pv_service,
                 virtual_switch_to_machine_connector,
                 dv_port_group_name_generator,
                 vlan_spec_factory,
                 vlan_id_range_parser):
        """
        :param py_service: vCenter API wrapper
        :param virtual_switch_to_machine_connector:
        :param dv_port_group_name_generator: DvPortGroupNameGenerator
        :param vlan_spec_factory: VlanSpecFactory
        :param vlan_id_range_parser: VLanIdRangeParser
        """
        self.pv_service = pv_service
        self.virtual_switch_to_machine_connector = virtual_switch_to_machine_connector
        self.dv_port_group_name_generator = dv_port_group_name_generator
        self.vlan_spec_factory = vlan_spec_factory
        self.vlan_id_range_parser = vlan_id_range_parser

    def connect_to_networks(self, si, logger, vm_uuid, vm_network_mappings, default_network_name,
                            reserved_networks, dv_switch_name):
        """
        Connect VM to Network
        :param si: VmWare Service Instance - defined connection to vCenter
        :param logger:
        :param vm_uuid: <str> UUID for VM
        :param vm_network_mappings: <collection of 'VmNetworkMapping'>
        :param default_network_name: <str> Full Network name - likes 'DataCenterName/NetworkName'
        :param reserved_networks:
        :param dv_switch_name: <str> Default dvSwitch name
        :return: None
        """
        vm = self.pv_service.find_by_uuid(si, vm_uuid)

        if not vm:
            raise ValueError('VM having UUID {0} not found'.format(vm_uuid))

        default_network_instance = self.pv_service.get_network_by_full_name(si, default_network_name)

        if not default_network_instance:
            raise ValueError('Default Network {0} not found'.format(default_network_name))

        mappings = self._prepare_mappings(dv_switch_name=dv_switch_name, vm_network_mappings=vm_network_mappings)

        updated_mappings = self.virtual_switch_to_machine_connector.connect_by_mapping(
            si, vm, mappings, default_network_instance, reserved_networks, logger)

        connection_results = []
        for updated_mapping in updated_mappings:

            connection_result = ConnectionResult(mac_address=updated_mapping.vnic.macAddress,
                                                 vnic_name=updated_mapping.vnic.deviceInfo.label,
                                                 requested_vnic=updated_mapping.requested_vnic,
                                                 vm_uuid=vm_uuid,
                                                 network_name=updated_mapping.network.name,
                                                 network_key=updated_mapping.network.key)
            connection_results.append(connection_result)

        return connection_results

    def _prepare_mappings(self, dv_switch_name, vm_network_mappings):
        mappings = []
        # create mapping
        for vm_network_mapping in vm_network_mappings:
            vm_network_mapping.dv_port_name = \
                self.dv_port_group_name_generator.generate_port_group_name(dv_switch_name,
                                                                           vm_network_mapping.vlan_id,
                                                                           vm_network_mapping.vlan_spec)

            vm_network_mapping.vlan_id = \
                self.vlan_id_range_parser.parse_vlan_id(vm_network_mapping.vlan_spec, vm_network_mapping.vlan_id)

            vm_network_mapping.vlan_spec = \
                self.vlan_spec_factory.get_vlan_spec(vm_network_mapping.vlan_spec)

            mappings.append(vm_network_mapping)
        return mappings
