from vCenterShell.vm.dvswitch_connector import VmNetworkMapping


class VirtualSwitchConnectCommand:
    def __init__(self, pv_service, virtual_switch_to_machine_connector,
                 dv_port_group_name_generator, vlan_spec_factory, vlan_id_range_parser, vcenter_resource_model,
                 helpers):
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
        self.vcenter_resource_model = vcenter_resource_model
        self.helpers = helpers

    def connect_vnic_to_network(self,
                                si,
                                vm_uuid,
                                vlan_id,
                                vlan_spec_type,
                                vnic_name=None,
                                dv_switch_path=None,
                                dv_switch_name=None,
                                port_group_path=None):
        vm = self.pv_service.find_by_uuid(si, vm_uuid)

        vnic_to_network_map = self.get_vnic_to_network_map(vnic_name, dv_switch_name, dv_switch_path, port_group_path,
                                                           vlan_id, vlan_spec_type)

        self.virtual_switch_to_machine_connector.connect_by_mapping(si, vm, [vnic_to_network_map])

    def connect_to_networks(self, si, vm_uuid, vm_network_mappings):
        vm = self.pv_service.find_by_uuid(si, vm_uuid)
        mappings = []
        for vm_network_mapping in vm_network_mappings:
            mappings.append(self.get_vnic_to_network_map(vm_network_mapping.vnic_name,
                                                         vm_network_mapping.dv_switch_name,
                                                         vm_network_mapping.dv_switch_path,
                                                         vm_network_mapping.port_group_path,
                                                         vm_network_mapping.vlan_id,
                                                         vm_network_mapping.vlan_spec_type))

        self.virtual_switch_to_machine_connector.connect_by_mapping(si, vm, mappings)

    def get_vnic_to_network_map(self, vnic_name, dv_switch_name, dv_switch_path, port_group_path, vlan_id,
                                vlan_spec_type):
        vnic_to_network_map = VmNetworkMapping()
        # set default if is None
        vnic_to_network_map.dv_switch_name, vnic_to_network_map.dv_switch_path, vnic_to_network_map.port_group_path = \
            self.set_default_if_none(dv_switch_name,
                                     dv_switch_path,
                                     port_group_path)
        # get the vm
        vnic_to_network_map.vlan_id_range = self.vlan_id_range_parser.parse_vlan_id(vlan_id)
        vnic_to_network_map.dv_port_name = self.dv_port_group_name_generator.generate_port_group_name(vlan_id)
        vnic_to_network_map.vlan_spec = self.vlan_spec_factory.get_vlan_spec(vlan_spec_type)

        vnic_to_network_map.vnic_name = vnic_name
        return vnic_to_network_map

    def set_default_if_none(self, dv_switch_name, dv_switch_path, port_group_path):
        if not dv_switch_path:
            dv_switch_path = self.vcenter_resource_model.default_dvswitch_path
        if not dv_switch_name:
            dv_switch_name = self.vcenter_resource_model.default_dvswitch_name
        if not port_group_path:
            port_group_path = self.vcenter_resource_model.default_port_group_path
        return dv_switch_name, dv_switch_path, port_group_path
