# -*- coding: utf-8 -*-

from pyVmomi import vim
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.network.network_specifications import network_is_standard, network_is_portgroup


class VNicService(object):
    def __init__(self):
        super(VNicService, self).__init__()

    @staticmethod
    def vnic_set_connectivity_status(nicspec, is_connected, logger):
        if not nicspec.device.connectable:
            nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
            nicspec.device.connectable.startConnected = is_connected

        nicspec.device.connectable.connected = is_connected
        logger.debug(u"vNIC {} set connected as '{}'".format(nicspec, is_connected))
        return nicspec

    @staticmethod
    def vnic_add_to_vm_task(nicspec, virtual_machine, logger):
        """
        Add new vNIC to VM
        :param nicspec: <vim.vm.device.VirtualDeviceSpec>
        :param virtual_machine:
        :param logger:
        :return:
        """
        if issubclass(type(nicspec), vim.vm.device.VirtualDeviceSpec):
            nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
            VNicService.vnic_set_connectivity_status(nicspec, True)
            logger.debug(u"Attaching new vNIC '{}' to VM '{}'...".format(nicspec, virtual_machine))
            task = pyVmomiService.vm_reconfig_task(virtual_machine, [nicspec])
            return task
        else:
            logger.warn(u"Cannot attach new vNIC '{}' to VM '{}'".format(nicspec, virtual_machine))
            return None

    @staticmethod
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

    @staticmethod
    def _network_get_network_by_connection(vm, port_connection, pyvmomi_service):
        # vim.dvs.PortConnection
        network_key = port_connection.portgroupKey
        network = pyvmomi_service.get_network_by_key_from_vm(vm, network_key)
        return network

    @staticmethod
    def vnic_get_network_attached(vm, device, pyvmomi_service, logger):
        """
        Get a Network connected to a particular Device (vNIC)
        @see https://github.com/vmware/pyvmomi/blob/master/docs/vim/dvs/PortConnection.rst

        :param vm:
        :param device: <vim.vm.device.VirtualVmxnet3> instance of adapter
        :param pyvmomi_service:
        :param logger:
        :return: <vim Network Obj or None>
        """

        try:
            backing = device.backing
            if hasattr(backing, 'network'):
                return backing.network
            elif hasattr(backing, 'port') and hasattr(backing.port, 'portgroupKey'):
                return VNicService._network_get_network_by_connection(vm, backing.port, pyvmomi_service)
        except:
            logger.debug(u"Cannot determinate which Network connected to device {}".format(device))
            return None

    @staticmethod
    def device_is_attached_to_network(device, network_name):
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

    @staticmethod
    def vnic_is_attachet_to_network(nicspec, network_name):
        """
        Checks if the vNIC has a backing with of the right network name

        :param nicspec: <vim.vm.device.VirtualDeviceSpec>
        :param <str> network_name: network name
        :return:
        """
        return VNicService.device_is_attached_to_network(nicspec.device, network_name)

    @staticmethod
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

    @staticmethod
    def vnic_attach_to_network_standard(nicspec, network, logger):
        """
        Attach vNIC to a 'usual' network
        :param nicspec: <vim.vm.device.VirtualDeviceSpec>
        :param network: <vim.Network>
        :param logger:
        :return: updated 'nicspec'
        """
        if nicspec and network_is_standard(network):
            network_name = network.name
            nicspec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
            nicspec.device.backing.network = network

            nicspec.device.wakeOnLanEnabled = True
            nicspec.device.deviceInfo = vim.Description()

            nicspec.device.backing.deviceName = network_name

            nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
            nicspec.device.connectable.startConnected = True
            nicspec.device.connectable.allowGuestControl = True

            logger.debug(u"Assigning network '{}' for vNIC".format(network_name))
        else:
            # logger.warn(u"Cannot assigning network '{}' for vNIC {}".format(network, nicspec))
            logger.warn(u"Cannot assigning network  for vNIC ".format(network, nicspec))
        return nicspec

    @staticmethod
    def vnic_attach_to_network_distributed(nicspec, port_group, logger):
        """
        Attach vNIC to a Distributed Port Group network
        :param nicspec: <vim.vm.device.VirtualDeviceSpec>
        :param port_group: <vim.dvs.DistributedVirtualPortgroup>
        :param logger:
        :return: updated 'nicspec'
        """
        if nicspec and network_is_portgroup(port_group):
            network_name = port_group.name

            dvs_port_connection = vim.dvs.PortConnection()
            dvs_port_connection.portgroupKey = port_group.key
            dvs_port_connection.switchUuid = port_group.config.distributedVirtualSwitch.uuid

            nicspec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
            nicspec.device.backing.port = dvs_port_connection

            logger.debug(u"Assigning portgroup '{}' for vNIC".format(network_name))
        else:
            logger.warn(u"Cannot assigning portgroup for vNIC")
        return nicspec

    @staticmethod
    def vnic_attached_to_network(nicspec, network, logger):
        """
        Attach vNIC to Network.
        :param nicspec: <vim.vm.device.VirtualDeviceSpec>
        :param network: <vim network obj>
        :return: updated 'nicspec'
        """

        if nicspec:
            if network_is_portgroup(network):
                return VNicService.vnic_attach_to_network_distributed(nicspec, network,
                                                                      logger=logger)
            elif network_is_standard(network):
                return VNicService.vnic_attach_to_network_standard(nicspec, network,
                                                                   logger=logger)
        return None

    @staticmethod
    def vnic_new_attached_to_network(network):
        """
        Compose new vNIC and attach it to Network.
        :param nicspec: <vim.vm.device.VirtualDeviceSpec>
        :param network: <vim network obj>
        :return: <vim.vm.device.VirtualDeviceSpec> ready for inserting to VM
        """
        return VNicService.vnic_attached_to_network(VNicService.vnic_compose_empty(), network, logger)

    @staticmethod
    def vnic_add_new_to_vm_task(vm, network, logger):
        """
        Compose new vNIC and attach it to VM & connect to Network
        :param nicspec: <vim.vm.VM>
        :param network: <vim network obj>
        :return: <Task>
        """

        nicspes = VNicService.vnic_new_attached_to_network(network)
        task = VNicService.vnic_add_to_vm_task(nicspes, vm, logger)
        return task

    @staticmethod
    def is_vnic_attached_to_network(device, network):
        if hasattr(device, 'backing'):
            if hasattr(device.backing, 'port') and hasattr(device.backing.port, 'portgroupKey'):
                return device.backing.port.portgroupKey == network.key
            if hasattr(device.backing, 'network') and hasattr(device.backing.network, 'name'):
                return device.backing.network.name == network.name
        return False

    @staticmethod
    def is_vnic_connected(vnic):
        is_connected = hasattr(vnic, 'connectable') and vnic.connectable.connected
        return is_connected

    @staticmethod
    def map_vnics(vm):
        """
        maps the vnic on the vm by name
        :param vm: virtual machine
        :return: dictionary: {'vnic_name': vnic}
        """
        return {device.deviceInfo.label: device
                for device in vm.config.hardware.device
                if isinstance(device, vim.vm.device.VirtualEthernetCard)}

    @staticmethod
    def get_device_spec(vnic, set_connected):
        """
        this function creates the device change spec,
        :param vnic: vnic
        :param set_connected: bool, set as connected or not, default: True
        :rtype: device_spec
        """
        nic_spec = VNicService.create_vnic_spec(vnic)
        VNicService.set_vnic_connectivity_status(nic_spec, to_connect=set_connected)
        return nic_spec

    @staticmethod
    def create_vnic_spec(device):
        """
        create device spec for existing device and the mode of edit for the vcenter to update
        :param device:
        :rtype: device spec
        """
        nic_spec = vim.vm.device.VirtualDeviceSpec()
        nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        nic_spec.device = device
        return nic_spec

    @staticmethod
    def set_vnic_connectivity_status(nic_spec, to_connect):
        """
            sets the device spec as connected or disconnected
            :param nic_spec: the specification
            :param to_connect: bool
            """
        nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic_spec.device.connectable.connected = to_connect
        nic_spec.device.connectable.startConnected = to_connect
