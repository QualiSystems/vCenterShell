# -*- coding: utf-8 -*-
"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info

@see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.DistributedVirtualSwitch.html
"""

from pyVmomi import vim
from common.vcenter.vmomi_service import *
from common.utilites.io import get_path_and_name
from vCenterShell.vm import vm_reconfig_task, vm_get_network_by_name
from vCenterShell.network.vnic.vnic_common import device_is_attached_to_network
from common.logger import getLogger

_logger = getLogger("vCenterShell")


class VirtualSwitchToMachineDisconnectCommand(object):
    def __init__(self,
                 pyvmomi_service,
                 connection_retriever,
                 port_group_configurer,
                 default_network):
        self.pyvmomi_service = pyvmomi_service
        self.connection_retriever = connection_retriever
        self.port_group_configurer = port_group_configurer
        self.default_network = default_network

        # self.synchronous_task_waiter = synchronous_task_waiter

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

        condition = lambda device: device_is_attached_to_network(device, network_name) if network_name else lambda \
            x: True
        return self.remove_interfaces_from_vm_task(vm, condition)

    def disconnect_all(self, vcenter_name, vm_uuid):
        return self.disconnect(vcenter_name, vm_uuid, None)

    def disconnect(self, vcenter_name, vm_uuid, network_name=None):
        """
        disconnect network adapter of the vm. If 'network_name' = None - disconnect ALL interfaces
        :param default_network_full_name:
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
        _logger.debug(u"Disconnect Interface VM: '{}' Network: '{}' ...".format(vm_uuid, network_name or "ALL"))

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        if network_name:
            network = vm_get_network_by_name(vm, network_name)
            if network is None:
                raise KeyError(u'Network not found ({0})'.format(network_name))
        else:
            network = None

        default_network = self.pyvmomi_service.get_network_by_full_name(si, self.default_network)
        if network:
            return self.port_group_configurer.disconnect_network(vm, network, default_network)
        else:
            return self.port_group_configurer.disconnect_all_networks(vm, default_network)

    def remove_interfaces_from_vm_task(self, virtual_machine, filter_function=None):
        """
        Remove interface from VM
        @see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.VirtualMachine.html#reconfigure
        :param virtual_machine: <vim.vm object>
        :param filter_function: function that gets the device and decide if it should be deleted
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
