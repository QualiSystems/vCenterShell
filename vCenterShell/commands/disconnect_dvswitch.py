# -*- coding: utf-8 -*-
"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info

@see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.DistributedVirtualSwitch.html
"""

from pyVmomi import vim

from common.vcenter.vmomi_service import *
from vCenterShell.vm import vm_reconfig_task
from common.logger import getLogger
_logger = getLogger("vCenterShell")


#todo move to some 'common' module
def get_path_and_name(full_name):
    """
    Split Whole Patch onto 'Patch' and 'Name'
    :param full_name: <str> Full Resource Name - likes 'Root/Folder/Folder2/Name'
    :return: tuple (Patch, Name)
    """
    if full_name:
        parts = full_name.split("/")
        return ("/".join(parts[0:-1]), parts[-1]) if len(parts) > 1 else ("/", full_name)
    return None, None


class VirtualSwitchToMachineDisconnectCommand(object):
    def __init__(self,
                 pyvmomi_service,
                 connection_retriever,
                 port_group_configurer):
        self.pyvmomi_service = pyvmomi_service
        self.connection_retriever = connection_retriever
        self.port_group_configurer = port_group_configurer

        #self.synchronous_task_waiter = synchronous_task_waiter

    #todo - NOT USED - REMOVE
    def remove_vnic(self, vcenter_name, vm_uuid, network_name=None):
        """
        disconnect all of the network adapter of the vm
        :param <str> network_name: the name of the specific network to disconnect & vNic remove
        :param <str> vcenter_name: the name of the vCenter to connect to
        :param <str> vm_uuid: the uuid of the vm
        :return:
        """
        connection_details = self.connection_retriever.connection_details(vcenter_name)

        si = self.pyvmomi_service.connect(connection_details.host, connection_details.username,
                                          connection_details.password,
                                          connection_details.port)
        _logger.debug("Revoking ALL Interfaces from VM '{}'".format(vm_uuid))

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        condition = lambda device: self.is_device_match_network(device, network_name) if network_name else lambda x: True
        return self.remove_interfaces_from_vm_task(vm, condition)

    #todo move to COMMON
    def get_network_by_name(self, vm, network_name):
        """
        Try to find Network scanning all attached to VM networks
        :param vm: <vim.vm>
        :param network_name: <str> name of network
        :return: <vim.vm.Network or None>
        """
        for network in vm.network:
            if network_name == network.name:
                return network
        return None

    #todo move to COMMON
    def get_network_by_full_name(self, si, default_network_full_name):
        """
        Find network by a Full Name
        :param default_network_full_name: <str> Full Network Name - likes 'Root/Folder/Network'
        :return:
        """
        path, name = get_path_and_name(default_network_full_name)
        return self.pyvmomi_service.find_network_by_name(si, path, name) if name else None


    def disconnect_all(self, vcenter_name, vm_uuid, network_name=None, default_network_full_name=None):
        return self.disconnect(vcenter_name, vm_uuid, None, default_network_full_name)

    def disconnect(self, vcenter_name, vm_uuid, network_name=None, default_network_full_name=None):
        """
        disconnect network adapter of the vm. If 'network_name' = None - disconnect ALL interfaces
        :param <str> vcenter_name: the name of the vCenter to connect to
        :param <str> vm_uuid: the uuid of the vm
        :param <str | None> default_network_name: the name of the network which will be attached against a disconnected one
        :param <str | None> network_name: the name of the specific network to disconnect
        :return: Started Task
        """
        connection_details = self.connection_retriever.connection_details(vcenter_name)

        si = self.pyvmomi_service.connect(connection_details.host,
                                          connection_details.username,
                                          connection_details.password,
                                          connection_details.port)
        _logger.debug("Revoking Interface from VM '{}'...".format(vm_uuid))

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        if network_name:
            network = self.get_network_by_name(vm, network_name)
            if network is None:
                raise KeyError('network not found ({0})'.format(network_name))
        else:
            network = None

        default_network = self.get_network_by_full_name(si, default_network_full_name)
        if network:
            return self.port_group_configurer.disconnect_network(vm, network, default_network, erase_network=True)

        else:
            return self.port_group_configurer.disconnect_all_networks(vm, default_network)

    def is_device_match_network(self, device, network_name):
        """
        checks if the device has a backing with of the right network name
        :param <vim.vm.Device> device: instance of adapter
        :param <str> network_name: network name
        :return:
        """
        backing = device.backing

        if hasattr(backing, 'network') and hasattr(backing.network, 'name'):
            return network_name == backing.network.name
        elif hasattr(backing, 'port') and hasattr(backing.port, 'portgroupKey'):
            return network_name == backing.port.portgroupKey
        return False

    #todo NOT USED but work OK - move to COMMON
    def remove_interfaces_from_vm_task(self, virtual_machine, filter_function=None):
        """
        @see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.VirtualMachine.html#reconfigure
        :param filter_function: function that gets the device and decide if it should be deleted
        :param virtual_machine: <vim.vm object>
        :return:
        """
        device_change = []
        for device in virtual_machine.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard) and \
                    (filter_function is None or filter_function(device)):
                nicspec = vim.vm.device.VirtualDeviceSpec()
                nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                nicspec.device = device
                device_change.append(nicspec)

        if len(device_change) > 0:
            return vm_reconfig_task(virtual_machine, device_change)
        return None

