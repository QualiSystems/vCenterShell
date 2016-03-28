# -*- coding: utf-8 -*-
"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info

@see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.DistributedVirtualSwitch.html
"""

from pyVmomi import vim
from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from cloudshell.cp.vcenter.vm.portgroup_configurer import VNicDeviceMapper


class VirtualSwitchToMachineDisconnectCommand(object):
    def __init__(self,
                 pyvmomi_service,
                 port_group_configurer,
                 resource_model_parser):
        """
        Disconnect Distributed Virtual Switch from VM Command
        :param pyvmomi_service: vCenter API wrapper
        :param port_group_configurer: Port Group Configurer Service
        :type port_group_configurer: cloudshell.cp.vcenter.vm.portgroup_configurer.VirtualMachinePortGroupConfigurer
        :param <ResourceModelParser> resource_model_parser: Network which disconnected interface will be attached to
        :return:
        """
        self.pyvmomi_service = pyvmomi_service
        self.port_group_configurer = port_group_configurer
        self.resource_model_parser = resource_model_parser

    def disconnect_from_networks(self, si, logger, vcenter_data_model, vm_uuid, vm_network_remove_mappings):

        default_network = VMLocation.combine(
            [vcenter_data_model.default_datacenter, vcenter_data_model.holding_network])

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)
        if not vm:
            raise ValueError('VM having UUID {0} not found'.format(vm_uuid))

        default_network = self.pyvmomi_service.get_network_by_full_name(si, default_network)

        mappings = []
        vnics = []
        for vm_network_remove_mapping in vm_network_remove_mappings:
            vnic = self.pyvmomi_service.get_vnic_by_mac_address(vm, vm_network_remove_mapping.mac_address)
            if vnic is None:
                raise KeyError('VNIC having MAC address {0} not found on VM having UUID {1}'
                               .format(vm_network_remove_mapping.mac_address, vm_uuid))

            vnics.append(vnic)
            mappings.append(VNicDeviceMapper(connect=False, network=default_network,
                                             requested_vnic=vm_network_remove_mapping.mac_address,
                                             vnic=vnic, mac=vm_network_remove_mapping.mac_address))

        networks_to_remove = self.port_group_configurer.get_networks_on_vnics(vm, vnics, logger)

        res = self.port_group_configurer.update_vnic_by_mapping(vm, mappings, logger)
        self.port_group_configurer.erase_network_by_mapping(networks_to_remove, vcenter_data_model.reserved_networks,
                                                            logger)
        return res

    def disconnect_all(self, si, logger, vcenter_data_model, vm_uuid, vm=None):
        return self.disconnect(si, vcenter_data_model, vm_uuid, logger,  None, None)

    def disconnect(self, si, logger, vcenter_data_model, vm_uuid, network_name=None, vm=None):
        """
        disconnect network adapter of the vm. If 'network_name' = None - disconnect ALL interfaces
        :param <str> si:
        :param logger:
        :param VMwarevCenterResourceModel vcenter_data_model:
        :param <str> vm_uuid: the uuid of the vm
        :param <str | None> network_name: the name of the specific network to disconnect
        :param <pyvmomi vm object> vm: If the vm obj is None will use vm_uuid to fetch the object
        :return: Started Task
        """
        logger.debug("Disconnect Interface VM: '{0}' Network: '{1}' ...".format(vm_uuid, network_name or "ALL"))
        if vm is None:
            vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)
            if not vm:
                return "Warning: failed to locate vm {0} in vCenter".format(vm_uuid)

        if network_name:
            network = self.pyvmomi_service.vm_get_network_by_name(vm, network_name)
            if network is None:
                raise KeyError('Network not found ({0})'.format(network_name))
        else:
            network = None

        network_full_name = VMLocation.combine(
            [vcenter_data_model.default_datacenter, vcenter_data_model.holding_network])

        default_network = self.pyvmomi_service.get_network_by_full_name(si, network_full_name)
        if network:
            return self.port_group_configurer.disconnect_network(vm, network, default_network,
                                                                 vcenter_data_model.reserved_networks,
                                                                 logger=logger)
        else:
            return self.port_group_configurer.disconnect_all_networks(vm, default_network,
                                                                      vcenter_data_model.reserved_networks,
                                                                      logger=logger)

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
