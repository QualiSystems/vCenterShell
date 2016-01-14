from unittest import TestCase

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from common.vcenter.task_waiter import SynchronousTaskWaiter
from common.vcenter.vmomi_service import pyVmomiService
from tests.utils.testing_credentials import TestCredentials
from vCenterShell.network.dvswitch.creator import DvPortGroupCreator
from vCenterShell.network.dvswitch.name_generator import DvPortGroupNameGenerator
from vCenterShell.network.vnic import vnic_common
from vCenterShell.vm.dvswitch_connector import VmNetworkMapping, VirtualSwitchToMachineConnector
from vCenterShell.vm.portgroup_configurer import VirtualMachinePortGroupConfigurer
from vCenterShell.vm.vnic_to_network_mapper import VnicToNetworkMapper


class VirtualSwitchToMachineCommandIntegrationTest(TestCase):

    def integration_test_connect(self):
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)
        synchronous_task_waiter = SynchronousTaskWaiter()
        mapper = VnicToNetworkMapper(DvPortGroupNameGenerator(), 'anetwork')
        dv_port_group_creator = DvPortGroupCreator(py_vmomi_service, synchronous_task_waiter)
        virtual_machine_port_group_configurer = VirtualMachinePortGroupConfigurer(py_vmomi_service,
                                                                                  synchronous_task_waiter,
                                                                                  mapper,
                                                                                  vnic_common)

        mapping = VmNetworkMapping()
        mapping.vlan_id = [vim.NumericRange(start=65, end=65)]
        mapping.dv_port_name = DvPortGroupNameGenerator().generate_port_group_name(65)
        mapping.dv_switch_name = 'dvSwitch'
        mapping.dv_switch_path = 'QualiSB'
        mapping.port_group_path = 'QualiSB'
        mapping.vlan_spec = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec()
        connector = VirtualSwitchToMachineConnector(
            dv_port_group_creator,
            virtual_machine_port_group_configurer)

        vm = py_vmomi_service.find_vm_by_name(si, 'QualiSB/Raz', '2')

        # Act
        connector.connect_by_mapping(si, vm, [mapping])

        pass
