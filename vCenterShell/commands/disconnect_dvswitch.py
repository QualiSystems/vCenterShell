# -*- coding: utf-8 -*-
"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info

@see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.DistributedVirtualSwitch.html
"""

from pyVmomi import vim
from pycommon.pyVmomiService import *
from pycommon.logger import getLogger

_logger = getLogger("vCenterShell")


class VirtualSwitchToMachineDisconnectCommand(object):
    def __init__(self,
                 pyvmomi_service,
                 connection_retriever,
                 synchronous_task_waiter):
        self.pyvmomi_service = pyvmomi_service
        self.connection_retriever = connection_retriever
        self.synchronous_task_waiter = synchronous_task_waiter

    def disconnect(self, vcenter_name, vm_uuid, network_name):
        """
        disconnect all of the network adapter of the vm
        :param <str> network_name: the name of the specific network to disconnect
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

        return self.remove_interfaces_from_vm(vm, lambda device: self.is_device_match_network(device, network_name))

    def disconnect_all(self, vcenter_name, vm_uuid):
        """
        disconnect all of the network adapter of the vm
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
        return self.remove_interfaces_from_vm(vm)

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

    def remove_interfaces_from_vm(self, virtual_machine, filter_function=None):
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
            return self.remove_devices(device_change, virtual_machine)
        return None

    def remove_devices(self, device_change, virtual_machine):
        """
        gets the adapters to remove from the vm and removes them
        :param <array<vim.vm.device.VirtualDeviceSpec>> device_change:  the adapters to remove
        :param <vim.VirtualMachine> virtual_machine:  the vm to remove the adapters from
        """
        config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
        task = virtual_machine.ReconfigVM_Task(config_spec)
        logger.info("Virtual Machine remove ALL Interfaces task STARTED")
        return self.synchronous_task_waiter.wait_for_task(task)
