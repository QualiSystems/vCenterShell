from unittest import TestCase

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import qualipy.scripts.cloudshell_scripts_helpers as helpers
from common.vcenter.task_waiter import SynchronousTaskWaiter
from common.vcenter.vmomi_service import pyVmomiService
from tests.utils.testing_credentials import TestCredentials
from vCenterShell.commands.connect_dvswitch import VirtualSwitchConnectCommand
from vCenterShell.network.dvswitch.creator import DvPortGroupCreator
from vCenterShell.network.dvswitch.name_generator import DvPortGroupNameGenerator
from vCenterShell.network.vlan.factory import VlanSpecFactory
from vCenterShell.network.vlan.range_parser import VLanIdRangeParser
from vCenterShell.network.vnic.vnic_service import VNicService
from vCenterShell.vm.dvswitch_connector import VmNetworkMapping, VirtualSwitchToMachineConnector
from vCenterShell.vm.portgroup_configurer import VirtualMachinePortGroupConfigurer
from vCenterShell.vm.vnic_to_network_mapper import VnicToNetworkMapper


class VirtualSwitchToMachineCommandIntegrationTest(TestCase):
    def integration_test_connect_A(self):
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)
        synchronous_task_waiter = SynchronousTaskWaiter()
        mapper = VnicToNetworkMapper(DvPortGroupNameGenerator())
        dv_port_group_creator = DvPortGroupCreator(py_vmomi_service, synchronous_task_waiter)
        virtual_machine_port_group_configurer = VirtualMachinePortGroupConfigurer(py_vmomi_service,
                                                                                  synchronous_task_waiter,
                                                                                  mapper,
                                                                                  VNicService())

        mapping = VmNetworkMapping()
        mapping.vlan_id = [vim.NumericRange(start=65, end=65)]
        mapping.dv_port_name = DvPortGroupNameGenerator().generate_port_group_name(65, 'Trunk')
        mapping.dv_switch_name = 'dvSwitch'
        mapping.dv_switch_path = 'QualiSB'
        mapping.port_group_path = 'QualiSB'
        mapping.vlan_spec = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec()
        connector = VirtualSwitchToMachineConnector(
            dv_port_group_creator,
            virtual_machine_port_group_configurer)

        vm = py_vmomi_service.find_vm_by_name(si, 'QualiSB/Raz', '2')

        # Act
        connector.connect_by_mapping(si, vm, [mapping], None)

        pass

    def integration_test_connect_B(self):
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)
        vm_uuid = py_vmomi_service.find_vm_by_name(si, 'QualiSB/Boris', 'Boris2-win7').config.uuid

        mapping = VmNetworkMapping()
        mapping.vlan_id = '114'
        # mapping.dv_port_name = 65
        mapping.dv_switch_name = 'dvSwitch'
        mapping.dv_switch_path = 'QualiSB'
        mapping.port_group_path = 'QualiSB'
        mapping.vlan_spec = 'Trunk'

        vlan_spec = VlanSpecFactory()
        range_fac = VLanIdRangeParser()
        synchronous_task_waiter = SynchronousTaskWaiter()
        name_gen = DvPortGroupNameGenerator()
        mapper = VnicToNetworkMapper(name_gen)
        dv_port_group_creator = DvPortGroupCreator(py_vmomi_service, synchronous_task_waiter)
        virtual_machine_port_group_configurer = VirtualMachinePortGroupConfigurer(py_vmomi_service,
                                                                                  synchronous_task_waiter,
                                                                                  mapper,
                                                                                  VNicService())
        connector = VirtualSwitchToMachineConnector(dv_port_group_creator, virtual_machine_port_group_configurer)

        command = VirtualSwitchConnectCommand(py_vmomi_service, connector, name_gen, vlan_spec, range_fac, Mock())

        command.connect_to_networks(si, vm_uuid, [mapping], 'QualiSB/anetwork')

    def test_integration(self):
        self.integration_test_connect_A()
        self.integration_test_connect_B()

    def test_dicconnect_bulk(self):
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)
        vm = py_vmomi_service.find_vm_by_name(si, 'QualiSB/Alex', 'test_25bf07ee')
        mac_address = '00:50:56:a2:5f:43'
        vnics = [device.backing.network for device in vm.config.hardware.device
                 if isinstance(device, vim.vm.device.VirtualEthernetCard)
                 and hasattr(device.backing, 'network')
                 and hasattr(device, 'macAddress')
                 and device.macAddress == mac_address]

        pass
