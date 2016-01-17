# -*- coding: utf-8 -*-
"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info

@see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.DistributedVirtualSwitch.html
"""

from pyVmomi import vim
from vCenterShell.network.vnic.vnic_service import VNicService
from common.logger import getLogger

_logger = getLogger("vCenterShell")


class VirtualSwitchToMachineDisconnectCommand(object):
    def __init__(self,
                 pyvmomi_service,
                 connection_retriever,
                 port_group_configurer,
                 default_network):
        """
        Disconnect Distributed Virtual Switch from VM Command
        :param pyvmomi_service: vCenter API wrapper
        :param connection_retriever: Service which provides connecting to vCenter
        :param port_group_configurer: Port Group Configurer Service
        :param <Network obj> default_network: Network which disconnected interface will be attached to
        :return:
        """
        self.pyvmomi_service = pyvmomi_service
        self.connection_retriever = connection_retriever
        self.port_group_configurer = port_group_configurer
        self.default_network = default_network

    def _get_service_instance(self, vcenter_name):
        """
        Get vCenter connection
        :return: VmWare SI (Service Instance)
        """
        connection_details = self.connection_retriever.connection_details()
        si = self.pyvmomi_service.connect(connection_details.host,
                                          connection_details.username,
                                          connection_details.password,
                                          connection_details.port)
        return si

    def remove_vnic(self, vcenter_name, vm_uuid, network_name=None):
        """
        disconnect all of the network adapter of the vm
        :param <str> network_name: the name of the specific network to disconnect & vNic remove
        :param <str> vcenter_name: the name of the vCenter to connect to
        :param <str> vm_uuid: the uuid of the vm
        :return:
        """
        _logger.debug(u"Revoking ALL Interfaces from VM '{}'...".format(vm_uuid))
        si = self._get_service_instance(vcenter_name)
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        condition = lambda device: VNicService.device_is_attached_to_network(device,
                                                                             network_name) if network_name else lambda \
                x: True
        return self.remove_interfaces_from_vm_task(vm, condition)

    def disconnect_all(self, vcenter_name, vm_uuid, vm=None):
        return self.disconnect(vcenter_name, vm_uuid, None)

    def disconnect(self, vcenter_name, vm_uuid, network_name=None, vm=None):
        """
        disconnect network adapter of the vm. If 'network_name' = None - disconnect ALL interfaces
        :param <str> vcenter_name: the name of the vCenter to connect to
        :param <str> vm_uuid: the uuid of the vm
        :param <str | None> network_name: the name of the specific network to disconnect
        :param <pyvmomi vm object> vm: If the vm obj is None will use vm_uuid to fetch the object
        :return: Started Task
        """
        _logger.debug(u"Disconnect Interface VM: '{}' Network: '{}' ...".format(vm_uuid, network_name or "ALL"))
        si = self._get_service_instance(vcenter_name)
        if vm is None:
            vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        if network_name:
            network = self.pyvmomi_service.vm_get_network_by_name(vm, network_name)
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
        :return: Task or None
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
            return self.pyvmomi_service.vm_reconfig_task(virtual_machine, device_change)
        return None
