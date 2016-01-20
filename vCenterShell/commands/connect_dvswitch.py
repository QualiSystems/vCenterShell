from models.ConnectionResult import ConnectionResult
from common.utilites.common_utils import get_object_as_string


class VirtualSwitchConnectCommand:
    def __init__(self,
                 pv_service,
                 virtual_switch_to_machine_connector,
                 dv_port_group_name_generator,
                 vlan_spec_factory,
                 vlan_id_range_parser,
                 logger):
        """
        :param py_service: vCenter API wrapper
        :param virtual_switch_to_machine_connector:
        :param dv_port_group_name_generator: DvPortGroupNameGenerator
        :param vlan_spec_factory: VlanSpecFactory
        :param vlan_id_range_parser: VLanIdRangeParser
        :param logger Logger
        """
        self.pv_service = pv_service
        self.virtual_switch_to_machine_connector = virtual_switch_to_machine_connector
        self.dv_port_group_name_generator = dv_port_group_name_generator
        self.vlan_spec_factory = vlan_spec_factory
        self.vlan_id_range_parser = vlan_id_range_parser
        self.logger = logger

    def connect_to_networks(self, si, vm_uuid, vm_network_mappings, default_network_name):
        """
        Connect VM to Network
        :param si: VmWare Service Instance - defined connection to vCenter
        :param vm_uuid: <str> UUID for VM
        :param vm_network_mappings: <collection of 'VmNetworkMapping'>
        :param default_network_name: <str> Full Network name - likes 'DataCenterName/NetworkName'
        :return: None
        """
        vm = self.pv_service.find_by_uuid(si, vm_uuid)

        if not vm:
            raise ValueError('VM having UUID {0} not found'.format(vm_uuid))

        default_network_instance = self.pv_service.get_network_by_full_name(si, default_network_name)

        mappings = self._prepare_mappings(vm_network_mappings)

        updated_mappings = self.virtual_switch_to_machine_connector.connect_by_mapping(
            si, vm, mappings, default_network_instance)

        connection_results = []
        for updated_mapping in updated_mappings:

            connection_result = ConnectionResult(mac_address=updated_mapping.vnic.macAddress,
                                                 vm_uuid=vm_uuid,
                                                 network_name=default_network_name)
            connection_results.append(connection_result)

        return connection_results

    def _prepare_mappings(self, vm_network_mappings):
        mappings = []
        # create mapping
        for vm_network_mapping in vm_network_mappings:
            vm_network_mapping.dv_port_name = \
                self.dv_port_group_name_generator.generate_port_group_name(vm_network_mapping.vlan_id)

            vm_network_mapping.vlan_id = \
                self.vlan_id_range_parser.parse_vlan_id(vm_network_mapping.vlan_spec, vm_network_mapping.vlan_id)

            vm_network_mapping.vlan_spec = \
                self.vlan_spec_factory.get_vlan_spec(vm_network_mapping.vlan_spec)

            mappings.append(vm_network_mapping)
        return mappings
