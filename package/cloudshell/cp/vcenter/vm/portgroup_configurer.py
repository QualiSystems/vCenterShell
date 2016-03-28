# -*- coding: utf-8 -*-

from cloudshell.cp.vcenter.common.logger import getLogger

from cloudshell.cp.vcenter.network.dvswitch.creator import DvPortGroupCreator
from cloudshell.cp.vcenter.network.network_specifications import network_is_portgroup
from threading import Lock
from pyVmomi import vim

logger = getLogger(__name__)


class VNicDeviceMapper(object):
    def __init__(self, vnic, requested_vnic, network, connect, mac):
        self.vnic = vnic
        self.requested_vnic = requested_vnic
        self.network = network
        self.connect = connect
        self.vnic_mac = mac


class VirtualMachinePortGroupConfigurer(object):
    def __init__(self,
                 pyvmomi_service,
                 synchronous_task_waiter,
                 vnic_to_network_mapper,
                 vnic_service,
                 name_gen):
        """
        :param pyvmomi_service: vCenter API wrapper
        :param synchronous_task_waiter: Task Performer Service
        :param vnic_to_network_mapper: VnicToNetworkMapper
        :param vnic_service: VNicService
        :return:
        """
        self.pyvmomi_service = pyvmomi_service
        self.synchronous_task_waiter = synchronous_task_waiter
        self.vnic_to_network_mapper = vnic_to_network_mapper
        self.vnic_service = vnic_service
        self.network_name_gen = name_gen
        self._lock = Lock()

    def connect_vnic_to_networks(self, vm, mapping, default_network, reserved_networks):
        vnic_mapping = self.vnic_service.map_vnics(vm)

        vnic_to_network_mapping = self.vnic_to_network_mapper.map_request_to_vnics(
            mapping, vnic_mapping, vm.network, default_network, reserved_networks)

        update_mapping = []
        for vnic_name, map in vnic_to_network_mapping.items():
            vnic = vnic_mapping[vnic_name]
            requseted_vnic = map[1]
            network = map[0]
            update_mapping.append(VNicDeviceMapper(vnic, requseted_vnic, network, True, vnic.macAddress))

        self.update_vnic_by_mapping(vm, update_mapping)
        return update_mapping

    def erase_network_by_mapping(self, networks, reserved_networks):
        nets = dict()
        self._lock.acquire()
        try:
            for net in networks:
                try:
                    nets[net.name] = net
                except vim.fault.ManagedObjectNotFound as e:
                    continue

                try:
                    for network in nets.values():
                        if self.network_name_gen.is_generated_name(network.name) \
                                and (not reserved_networks or network.name not in reserved_networks) \
                                and not network.vm:

                            task = self.destroy_port_group_task(network)
                            if task:
                                self.synchronous_task_waiter.wait_for_task(task=task,
                                                                           action_name='Erase dv Port Group')
                except vim.fault.ManagedObjectNotFound as e:
                    continue
        finally:
            self._lock.release()

    def disconnect_all_networks(self, vm, default_network, reserved_networks):
        vnics = self.vnic_service.map_vnics(vm)
        network_for_removal = self.get_networks_on_vnics(vm, vnics.values())
        update_mapping = [VNicDeviceMapper(vnic, vnic, default_network, False, vnic.macAddress) for vnic in
                          vnics.values()]
        res = self.update_vnic_by_mapping(vm, update_mapping)
        self.erase_network_by_mapping(network_for_removal, reserved_networks)
        return res

    def get_networks_on_vnics(self, vm, vnics):
        return [self.vnic_service.vnic_get_network_attached(vm, vnic, self.pyvmomi_service)
                for vnic in vnics]

    def create_mappings_for_all_networks(self, vm, default_network):
        vnics = self.vnic_service.map_vnics(vm)
        return [VNicDeviceMapper(vnic, vnic, default_network, False, vnic.macAddress) for vnic in vnics.values()]

    def create_mapping_for_network(self, vm, network, default_network):
        condition = lambda vnic: True if default_network else self.vnic_service.is_vnic_connected(vnic)
        vnics = self.vnic_service.map_vnics(vm)

        mapping = [VNicDeviceMapper(vnic, vnic_name, default_network, False, vnic.macAddress)
                   for vnic_name, vnic in vnics.items()
                   if self.vnic_service.is_vnic_attached_to_network(vnic, network) and condition(vnic)]
        return mapping

    def disconnect_network(self, vm, network, default_network, reserved_networks):
        condition = lambda vnic: True if default_network else self.vnic_service.is_vnic_connected(vnic)
        vnics = self.vnic_service.map_vnics(vm)
        network_to_remove = self.get_networks_on_vnics(vm, vnics.values())
        mapping = [VNicDeviceMapper(vnic, vnic_name, default_network, False, vnic.macAddress)
                   for vnic_name, vnic in vnics.items()
                   if self.vnic_service.is_vnic_attached_to_network(vnic, network) and condition(vnic)]

        res = self.update_vnic_by_mapping(vm, mapping)
        self.erase_network_by_mapping(network_to_remove, reserved_networks)
        return res

    def update_vnic_by_mapping(self, vm, mapping):
        vnics_change = []
        for item in mapping:
            spec = self.vnic_service.vnic_compose_empty(item.vnic)
            self.vnic_service.vnic_attached_to_network(spec, item.network)
            spec = self.vnic_service.get_device_spec(item.vnic, item.connect)
            vnics_change.append(spec)
        logger.debug('reconfiguring vm: {0} with: {1}'.format(vm, vnics_change))
        self.reconfig_vm(vnics_change, vm)
        return mapping

    def reconfig_vm(self, device_change, vm):
        logger.info("Changing network...")
        task = self.pyvmomi_service.vm_reconfig_task(vm, device_change)
        logger.debug('reconfigure task: {0}'.format(task.info))
        res = self.synchronous_task_waiter.wait_for_task(task=task,
                                                         action_name='Reconfigure VM')
        if res:
            logger.debug('reconfigure task result {0}'.format(res))
        return res

    @staticmethod
    def destroy_port_group_task(network):
        if network_is_portgroup(network):
            task = DvPortGroupCreator.dv_port_group_destroy_task(network)
            return task
        return None
