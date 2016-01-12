

class VirtualSwitchConnectCommand:
    def __init__(self, pv_service, virtual_switch_to_machine_connector,
                 dv_port_group_name_generator, vlan_spec_factory, vlan_id_range_parser):
        """
        :type pv_service: object
        :param virtual_switch_to_machine_connector:
        :param dv_port_group_name_generator: DvPortGroupNameGenerator
        :param vlan_spec_factory: VlanSpecFactory
        """
        self.pv_service = pv_service
        self.virtual_switch_to_machine_connector = virtual_switch_to_machine_connector
        self.dv_port_group_name_generator = dv_port_group_name_generator
        self.vlan_spec_factory = vlan_spec_factory  # type: VlanSpecFactory
        self.vlan_id_range_parser = vlan_id_range_parser

    def connect_to_networks(self, si, vm_uuid, vm_network_mappings):
        vm = self.pv_service.find_by_uuid(si, vm_uuid)
        mappings = []
        # create mapping
        for vm_network_mapping in vm_network_mappings:
            vm_network_mapping.vlan_id_range = \
                self.vlan_id_range_parser.parse_vlan_id(vm_network_mapping.vlan_id)
            vm_network_mapping.dv_port_name = \
                self.dv_port_group_name_generator.generate_port_group_name(vm_network_mapping.vlan_id)
            vm_network_mapping.vlan_spec = \
                self.vlan_spec_factory.get_vlan_spec(vm_network_mapping.vlan_spec)
            mappings.append(vm_network_mapping)

        self.virtual_switch_to_machine_connector.connect_by_mapping(si, vm, mappings)

