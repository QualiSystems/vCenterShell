# -*- coding: utf-8 -*-

from pyVmomi import vim
from common.vcenter.vmomi_service import *
from vCenterShell.network import network_is_portgroup
from vCenterShell.network.dvswitch.creator import DvPortGroupCreator


class VNicDeviceMapper(object):
    def __init__(self, vnic, network, connect):
        self.vnic = vnic
        self.network = network
        self.connect = connect


class VirtualMachinePortGroupConfigurer(object):
    def __init__(self,
                 pyvmomi_service,
                 synchronous_task_waiter,
                 vnic_to_network_mapper,
                 vnic_service):
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

    def connect_vnic_to_networks(self, vm, mapping, default_network):
        vnic_mapping = self.vnic_service.map_vnics(vm)

        vnic_to_network_mapping = self.vnic_to_network_mapper.map_request_to_vnics(
            mapping, vnic_mapping, vm.network, default_network)

        update_mapping = []
        for vnic_name, network in vnic_to_network_mapping.items():
            vnic = vnic_mapping[vnic_name]
            update_mapping.append(VNicDeviceMapper(vnic, network, True))

        self.update_vnic_by_mapping(vm, update_mapping)
        return update_mapping

    def erase_network_by_mapping(self, vm, update_mapping):
        for item in update_mapping:
            network = item[1] or self.vnic_service.vnic_get_network_attached(vm, item[0], self.pyvmomi_service)
            if network:
                task = self.destroy_port_group_task(network)
                if task:
                    try:
                        self.synchronous_task_waiter.wait_for_task(task=task,
                                                                   action_name='Erase dv Port Group')
                    except vim.fault.ResourceInUse:
                        pass
                        logger.debug(u"Port Group '{}' cannot be destroyed because of it using".format(network))

    def disconnect_all_networks(self, vm, default_network):
        vnics = self.vnic_service.map_vnics(vm)
        update_mapping = [VNicDeviceMapper(vnic, default_network, False) for vnic in vnics.values()]
        return self.update_vnic_by_mapping(vm, update_mapping)

    def disconnect_network(self, vm, network, default_network):
        condition = lambda vnic: True if default_network else self.vnic_service.is_vnic_connected(vnic)
        vnics = self.vnic_service.map_vnics(vm)

        mapping = [VNicDeviceMapper(vnic, default_network, False)
                   for vnic_name, vnic in vnics.items()
                   if self.vnic_service.is_vnic_attached_to_network(vnic, network) and condition(vnic)]

        return self.update_vnic_by_mapping(vm, mapping)

    def update_vnic_by_mapping(self, vm, mapping):
        vnics_change = []
        for item in mapping:
            spec = self.vnic_service.vnic_compose_empty(item.vnic)
            self.vnic_service.vnic_attached_to_network(spec, item.network)
            spec = self.vnic_service.get_device_spec(item.vnic, item.connect)
            vnics_change.append(spec)

        return self.reconfig_vm(vnics_change, vm)

    def reconfig_vm(self, device_change, vm):
        logger.info("Changing network...")
        task = self.pyvmomi_service.vm_reconfig_task(vm, device_change)
        return self.synchronous_task_waiter.wait_for_task(task=task,
                                                          action_name='Reconfigure VM')

    @staticmethod
    def destroy_port_group_task(network):
        if network_is_portgroup(network):
            task = DvPortGroupCreator.dv_port_group_destroy_task(network)
            return task
        return None
