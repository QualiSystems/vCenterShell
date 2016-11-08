
class VmNetworkMapping(object):
    def __init__(self):
        self.vnic_name = ''
        self.dv_port_name = ''
        self.dv_switch_name = ''
        self.dv_switch_path = ''
        self.vlan_id = ''
        self.vlan_spec = ''


class VmNetworkRemoveMapping(object):
    def __init__(self):
        self.vnic_name = ''
        self.network_name = ''


class ConnectRequest(object):
    def __init__(self, vnic_name, network):
        """
        model for the reconfigure request
        :param vnic_name: str
        :param network: vim.Network
        """
        self.vnic_name = vnic_name
        self.network = network


class VirtualSwitchToMachineConnector(object):
    def __init__(self,
                 dv_port_group_creator,
                 virtual_machine_port_group_configurer):
        """
        :param dv_port_group_creator: <DvPortGroupCreator> instance/interface
        :param virtual_machine_port_group_configurer: <VirtualMachinePortGroupConfigurer> instance/interface
        :type virtual_machine_port_group_configurer: cloudshell.cp.vcenter.vm.portgroup_configurer.VirtualMachinePortGroupConfigurer
        :return:
        """
        self.dv_port_group_creator = dv_port_group_creator
        self.virtual_machine_port_group_configurer = virtual_machine_port_group_configurer

    def connect_by_mapping(self, si, vm, mapping, default_network, reserved_networks, logger):
        """
        gets the mapping to the vnics and connects it to the vm
        :param default_network:
        :param si: ServiceInstance
        :param vm: vim.VirtualMachine
        :param mapping: [VmNetworkMapping]
        :param reserved_networks:
        :param logger:
        """
        request_mapping = []

        logger.debug(
            'about to map to the vm: {0}, the following networks'.format(vm.name if vm.name else vm.config.uuid))

        for network_map in mapping:
            network = self.dv_port_group_creator.get_or_create_network(si,
                                                                       vm,
                                                                       network_map.dv_port_name,
                                                                       network_map.dv_switch_name,
                                                                       network_map.dv_switch_path,
                                                                       network_map.vlan_id,
                                                                       network_map.vlan_spec,
                                                                       logger=logger)

            request_mapping.append(ConnectRequest(network_map.vnic_name, network))

        logger.debug(str(request_mapping))
        return self.virtual_machine_port_group_configurer.connect_vnic_to_networks(vm,
                                                                                   request_mapping,
                                                                                   default_network,
                                                                                   reserved_networks,
                                                                                   logger)

