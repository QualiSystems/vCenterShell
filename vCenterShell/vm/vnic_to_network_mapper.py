class VnicToNetworkMapper(object):
    def __init__(self, quali_name_generator, default_network):
        self.quali_name_generator = quali_name_generator
        self.default_network = default_network

    def map_request_to_vnics(self, requests, vnics, existing_network):
        mapping = dict()
        vnics_to_network_mapping = self.map_vnic_to_network(vnics, existing_network)
        for request in requests:
            if request.vnic_name:
                if not vnics_to_network_mapping[request.vnic_name]:
                    raise Exception('the vnic: {0} does not exist'.format(request.vnic))
                mapping[request.vnic] = request.network_spec
            else:
                vnic_name = self.find_available_vnic(vnics_to_network_mapping)
                mapping[vnic_name] = request.network_spec

        return mapping

    def find_available_vnic(self, vnics_to_network_mapping):
        for vnic_name, network_name in vnics_to_network_mapping.items():
            if network_name == self.default_network:
                return vnic_name
        raise Exception('no vnic available')

    def map_vnic_to_network(self, vnics, existing_network):
        mapping = dict()
        for vnic_name, vnic in vnics.items():
            if hasattr(vnic, 'backing'):
                if hasattr(vnic.backing, 'network') and hasattr(vnic.backing.network, 'name'):
                    network_to_map = vnic.backing.name
                elif hasattr(vnic.backing, 'port') and hasattr(vnic.backing.port, 'key'):
                    network_to_map = self.get_network_name_from_key(vnic.backing.port.key, existing_network)

            if not self.quali_name_generator.is_generated_name(network_to_map):
                network_to_map = self.default_network
            mapping[vnic_name] = network_to_map

        if mapping:
            return mapping
        raise Exception('there is no vnics')

    def get_network_name_from_key(self, key, existing_network):
        for network in existing_network:
            if hasattr(network, 'name') and hasattr(network, 'portgroupKey') and network.portgroupKey == key:
                return network.name
        return self.default_network
