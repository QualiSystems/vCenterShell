from unittest import TestCase
from mock import Mock
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from vCenterShell.commands.DvPortGroupCreator import DvPortGroupCreator
from vCenterShell.models.VCenterConnectionDetails import VCenterConnectionDetails
from vCenterShell.pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter
from tests.testCredentials import TestCredentials
from vCenterShell.commands.VirtualSwitchToMachineConnector import *


class TestVirtualSwitchToMachineConnector(TestCase):
    def test_integrationtest(self):
        resource_connection_details_retriever = Mock()
        credentials = TestCredentials()
        resource_connection_details_retriever.connection_details = Mock(
                return_value=VCenterConnectionDetails(credentials.host, credentials.username, credentials.password))
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        synchronous_task_waiter = SynchronousTaskWaiter()
        dv_port_group_creator = DvPortGroupCreator(py_vmomi_service, synchronous_task_waiter)
        virtual_switch_to_machine_connector = VirtualSwitchToMachineConnector(py_vmomi_service,
                                                                              resource_connection_details_retriever,
                                                                              dv_port_group_creator,
                                                                              synchronous_task_waiter)

        si = py_vmomi_service.connect(credentials.host, credentials.username,
                                      credentials.password,
                                      credentials.port)

        # vm = py_vmomi_service.find_vm_by_name(si, 'qs-srv-vcenter1.qualisystems.local\\QualiSB\\Boris', 'boris1')
        vm = py_vmomi_service.get_obj(si.content, [vim.VirtualMachine], 'boris1')
        virtual_machine_name = vm.summary.config.name
        vm_uuid = vm.config.uuid

        vlan_id = 'VLAN 1-DVUplinks-9203'
        # virtual_machine_name = 'boris1'
        virtual_machine_path = 'Boris'
        dv_switch_path = 'QualiSB'
        dv_switch_name = 'dvSwitch'
        dv_port_name = 'boris_group14'
        network_name = 'VM Network'
        virtual_switch_to_machine_connector.connect(virtual_machine_name, dv_switch_path, dv_switch_name,
                                                    dv_port_name, virtual_machine_path, vm_uuid,
                                                    network_name)

        # print port_group
