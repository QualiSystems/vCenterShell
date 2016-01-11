# -*- coding: utf-8 -*-

from pyVmomi import vim

from common.vcenter.vmomi_service import *
from vCenterShell.network import network_is_portgroup
from vCenterShell.vm import vm_reconfig_task


class VirtualMachinePortGroupConfigurer(object):
    def __init__(self, pyvmomi_service, synchronous_task_waiter, vnic_to_network_mapper, vnic_common):
        self.pyvmomi_service = pyvmomi_service
        self.synchronous_task_waiter = synchronous_task_waiter
        self.vnic_to_network_mapper = vnic_to_network_mapper
        self.vnic_common = vnic_common

    def connect(self, vm, mapping):
        vnic_mapping = self.map_vnics(vm)
        vnic_to_network_mapping = self.vnic_to_network_mapper.map_request_to_vnics(mapping, vnic_mapping, vm.network)
        update_mapping = []
        for vnic_name, network in vnic_to_network_mapping.items():
            vnic = vnic_mapping[vnic_name]
            update_mapping.append((vnic, network, True))

        self.update_vnic_by_mapping(vm, update_mapping)

    def erase_network_by_mapping(self, vm, update_mapping):
        for item in update_mapping:
            network = item[1] or vnic_get_network_attached(vm, item[0], self.pyvmomi_service)
            if network:
                task = self.destroy_port_group_task(network)
                if task:
                    try:
                        self.synchronous_task_waiter.wait_for_task(task)
                    except vim.fault.ResourceInUse:
                        pass
                        logger.debug(u"Port Group '{}' cannot be destroyed because of it using".format(network))

    def disconnect_all_networks(self, vm, default_network=None, erase_network=False):
        vnics = self.map_vnics(vm)
        update_mapping = [(vnic, None, False, default_network,) for vnic in vnics.values()]
        self.update_vnic_by_mapping(vm, update_mapping)
        if erase_network:
            self.erase_network_by_mapping(vm, update_mapping)
        return None

    def disconnect_network(self, vm, network, default_network=None, erase_network=False):
        condition = lambda vnic: True if default_network else not self.vnic_common.is_vnic_disconnected(vnic)
        vnics = self.vnic_common.map_vnics(vm)

        update_mapping = [(vnic, network, False, default_network,)
                          for vnic_name, vnic in vnics.items()
                          if self.vnic_common.is_vnic_attached_to_network(vnic, network) and condition(vnic)]

        self.update_vnic_by_mapping(vm, update_mapping)
        if erase_network:
            self.erase_network_by_mapping(vm, update_mapping)
        return None

    def update_vnic_by_mapping(self, vm, mapping):
        if not vm or not mapping:
            return None

        vnics_change = []
        for vnic, network, connect, default_network in mapping:
            network = default_network if default_network else network
            vnic_spec = self.vnic_common.vnic_compose_empty(vnic)
            self.vnic_common.vnic_attached_to_network(vnic_spec, network)
            vnic_spec = self.vnic_common.get_device_spec(vnic, connect)
            vnics_change.append(vnic_spec)

        return self.reconfig_vm(vnics_change, vm)

    def reconfig_vm(self, device_change, vm):
        logger.info("Changing network...")
        task = vm_reconfig_task(vm, device_change)
        return self.synchronous_task_waiter.wait_for_task(task)

    @staticmethod
    def destroy_port_group_task(network):
        from vCenterShell.network.dvswitch.creator import DvPortGroupCreator
        if network_is_portgroup(network):
            task = DvPortGroupCreator.dv_port_group_destroy_task(network)
            return task
        return None
