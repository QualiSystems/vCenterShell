class VnicToNetworkMapper(object):
    def __init__(self, quali_name_generator):
        self.quali_name_generator = quali_name_generator

    def map_request_to_vnics(self, requests, vnics, existing_network, default_network):
        """
        gets the requests for connecting netwoks and maps it the suitable vnic of specific is not specified
        :param requests:
        :param vnics:
        :param existing_network:
        :param default_network:
        :return:
        """
        mapping = dict()
        vnics_to_network_mapping = self._map_vnic_to_network(vnics, existing_network, default_network)
        for request in requests:
            if request.vnic_name:
                if not vnics_to_network_mapping[request.vnic_name]:
                    raise Exception('the vnic: {0} does not exist'.format(request.vnic))
                mapping[request.vnic_name] = request.network
                vnics_to_network_mapping.pop(request.vnic_name)
            else:
                vnic_name = self._find_available_vnic(vnics_to_network_mapping, default_network)
                mapping[vnic_name] = request.network
                vnics_to_network_mapping.pop(vnic_name)

        return mapping

    def _find_available_vnic(self, vnics_to_network_mapping, default_network):
        for vnic_name, network_name in vnics_to_network_mapping.items():
            if network_name == default_network.name:
                return vnic_name
        raise Exception('no vnic available')

    def _map_vnic_to_network(self, vnics, existing_network, default_network):
        mapping = dict()
        for vnic_name, vnic in vnics.items():
            network_to_map = ''
            if hasattr(vnic, 'backing'):
                if hasattr(vnic.backing, 'network') and hasattr(vnic.backing.network, 'name'):
                    network_to_map = vnic.backing.network.name
                elif hasattr(vnic.backing, 'port') and hasattr(vnic.backing.port, 'portgroupKey'):
                    network_to_map = self._get_network_name_from_key(vnic.backing.port.portgroupKey,
                                                                     existing_network, default_network)

            if not self.quali_name_generator.is_generated_name(network_to_map):
                network_to_map = default_network.name
            mapping[vnic_name] = network_to_map

        if mapping:
            return mapping
        raise Exception('there is no vnics')

    @staticmethod
    def _get_network_name_from_key(key, existing_network, default_network):
        for network in existing_network:
            if hasattr(network, 'name') and hasattr(network, 'key') and network.key == key:
                return network.name
        return default_network
