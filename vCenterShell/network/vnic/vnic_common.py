# -*- coding: utf-8 -*-

"""
The most common network/vNIC staff
@see https://github.com/vmware/pyvmomi-community-samples/issues/9
"""

from pyVmomi import vim

from vCenterShell.network import *
from common.logger import getLogger
logger = getLogger("vCenterCommon")


#todo move to more suitable place
def vm_reconfig_task(vm, device_change):
    config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
    task = vm.ReconfigVM_Task(config_spec)
    return task


def vnic_set_connectivity_status(nicspec, is_connected):
    if not nicspec.device.connectable:
        nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nicspec.device.connectable.startConnected = is_connected

    nicspec.device.connectable.connected = is_connected
    _logger.debug(u"vNIC {} set connected as '{}'".format(nicspec, is_connected))
    return nicspec


def vnic_add_to_vm_task(nicspec, virtual_machine):
    """
    Add new vNIC to VM
    :param nicspec: <vim.vm.device.VirtualDeviceSpec>
    :param virtual_machine:
    :return:
    """
    if issubclass(type(nicspec), vim.vm.device.VirtualDeviceSpec):
        nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        vnic_set_connectivity_status(nicspec, True)
        _logger.debug(u"Attaching new vNIC '{}' to VM '{}'...".format(nicspec, virtual_machine))
        task = vm_reconfig_task(virtual_machine, [nicspec])
        return task
    else:
        _logger.warn(u"Cannot attach new vNIC '{}' to VM '{}'".format(nicspec, virtual_machine))
        return None


def vnic_remove_from_vm_list(virtual_machine, filter_function=None):
    """
    @see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.VirtualMachine.html#reconfigure
    :param filter_function: function that gets the device and decide if it should be deleted
    :param virtual_machine: <vim.vm object>
    :return: <list of vim.vm.device.VirtualDeviceSpec> for 'ReconfigVM_Task' applying
    """
    device_change = []
    for device in virtual_machine.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualEthernetCard) and \
                (filter_function is None or filter_function(device)):
            nicspec = vim.vm.device.VirtualDeviceSpec()
            nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
            nicspec.device = device
            device_change.append(nicspec)

    return device_change


def device_is_attachet_to_network(device, network_name):
    """
    Checks if the device has a backing with of the right network name
    :param <vim.vm.Device> device: instance of adapter
    :param <str> network_name: network name
    :return:
    """

    try:
        backing = device.backing
    except:
        return False
    if hasattr(backing, 'network') and hasattr(backing.network, 'name'):
        return network_name == backing.network.name
    elif hasattr(backing, 'port') and hasattr(backing.port, 'portgroupKey'):
        return network_name == backing.port.portgroupKey

    return False


def vnic_is_attachet_to_network(nicspec, network_name):
    """
    Checks if the vNIC has a backing with of the right network name

    :param nicspec: <vim.vm.device.VirtualDeviceSpec>
    :param <str> network_name: network name
    :return:
    """
    return device_is_attachet_to_network(nicspec.device, network_name)


def vnic_compose_empty(device=None):
    """
    Compose empty vNIC for next attaching to a network
    :param device: <vim.vm.device.VirtualVmxnet3 or None> Device for this this 'spec' will be composed.
        If 'None' a new device will be composed.
        'Operation' - edit/add' depends on if device existed
    :return: <vim.vm.device.VirtualDeviceSpec>
    """
    nicspec = vim.vm.device.VirtualDeviceSpec()

    if device:
        nicspec.device = device
        nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    else:
        nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        nicspec.device = vim.vm.device.VirtualVmxnet3()
        nicspec.device.wakeOnLanEnabled = True
        nicspec.device.deviceInfo = vim.Description()

        nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nicspec.device.connectable.startConnected = True
        nicspec.device.connectable.allowGuestControl = True

    return nicspec


def vnic_attach_to_network_standard(nicspec, network):
    """
    Attach vNIC to a 'usual' network
    :param nicspec: <vim.vm.device.VirtualDeviceSpec>
    :param network: <vim.Network>
    :return: updated 'nicspec'
    """
    if nicspec and network_is_standard(network):
        network_name = network.name
        nicspec.device.deviceInfo.label = network_name
        nicspec.device.deviceInfo.summary = network_name
        nicspec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        nicspec.device.backing.network = network

        nicspec.device.wakeOnLanEnabled = True
        nicspec.device.deviceInfo = vim.Description()

        nicspec.device.backing.deviceName = network_name

        nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nicspec.device.connectable.startConnected = True
        nicspec.device.connectable.allowGuestControl = True

        _logger.debug(u"Assigning network '{}' for vNIC".format(network_name))
    else:
        #_logger.warn(u"Cannot assigning network '{}' for vNIC {}".format(network, nicspec))
        _logger.warn(u"Cannot assigning network  for vNIC ".format(network, nicspec))
    return nicspec


def vnic_attach_to_network_distributed(nicspec, port_group):
    """
    Attach vNIC to a Distributed Port Group network
    :param nicspec: <vim.vm.device.VirtualDeviceSpec>
    :param network: <vim.dvs.DistributedVirtualPortgroup>
    :return: updated 'nicspec'
    """
    if nicspec and network_is_portgroup(port_group):
        network_name = port_group.name
        #port.portgroupKey
        nicspec.device.deviceInfo.label = network_name
        nicspec.device.deviceInfo.summary = network_name

        dvs_port_connection = vim.dvs.PortConnection()
        dvs_port_connection.portgroupKey = port_group.key
        dvs_port_connection.switchUuid = port_group.config.distributedVirtualSwitch.uuid

        nicspec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        nicspec.device.backing.port = dvs_port_connection
        #nicspec.device.backing.deviceName - only for Standard Network makes sense
        _logger.debug (u"Assigning portgroup '{}' for vNIC".format(network_name))
    else:
        #_logger.warn(u"Cannot assigning portgroup '{}' for vNIC {}".format(port_group, nicspec))
        _logger.warn(u"Cannot assigning portgroup for vNIC")
    return nicspec


def vnic_attached_to_network(nicspec, network):
    """
    Attach vNIC to Network.
    :param nicspec: <vim.vm.device.VirtualDeviceSpec>
    :param network: <vim network obj>
    :return: updated 'nicspec'
    """

    if nicspec:
        if network_is_portgroup(network):
            return vnic_attach_to_network_distributed(nicspec, network)
        elif network_is_standard(network):
            return vnic_attach_to_network_standard(nicspec, network)
    return None


def vnic_new_attached_to_network(network):
    """
    Compose new vNIC and attach it to Network.
    :param nicspec: <vim.vm.device.VirtualDeviceSpec>
    :param network: <vim network obj>
    :return: <vim.vm.device.VirtualDeviceSpec> ready for inserting to VM
    """
    return vnic_attached_to_network(vnic_compose_empty(), network)




# (vim.vm.device.VirtualVmxnet3) {
#    dynamicType = <unset>,
#    dynamicProperty = (vmodl.DynamicProperty) [],
#    key = 4000,
#    deviceInfo = (vim.Description) {
#       dynamicType = <unset>,
#       dynamicProperty = (vmodl.DynamicProperty) [],
#       label = 'Network adapter 1',
#       summary = 'Anetwork'
#    },
#    backing = (vim.vm.device.VirtualEthernetCard.NetworkBackingInfo) {
#       dynamicType = <unset>,
#       dynamicProperty = (vmodl.DynamicProperty) [],
#       deviceName = 'Anetwork',
#       useAutoDetect = false,
#       network = 'vim.Network:network-2554',
#       inPassthroughMode = <unset>
#    },
#    connectable = (vim.vm.device.VirtualDevice.ConnectInfo) {
#       dynamicType = <unset>,
#       dynamicProperty = (vmodl.DynamicProperty) [],
#       startConnected = true,
#       allowGuestControl = true,
#       connected = false,
#       status = 'untried'
#    },
#    slotInfo = <unset>,
#    controllerKey = 100,
#    unitNumber = 7,
#    addressType = 'assigned',
#    macAddress = '00:50:56:a2:11:0d',
#    wakeOnLanEnabled = true,
#    resourceAllocation = <unset>,
#    externalId = <unset>,
#    uptCompatibilityEnabled = <unset>
# }