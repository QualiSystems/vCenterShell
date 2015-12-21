from unittest import TestCase
from mock import Mock
from pyVim.connect import SmartConnect, Disconnect
from vCenterShell.models.VCenterConnectionDetails import VCenterConnectionDetails
from vCenterShell.pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter
from tests.testCredentials import TestCredentials
from vCenterShell.commands.VirtualSwitchToMachineConnector import *


class TestVirtualSwitchToMachineConnector(TestCase):
    def integrationtest(self):
        resource_connection_details_retriever = Mock()
        credentials = TestCredentials()
        resource_connection_details_retriever.connection_details = Mock(
                return_value=VCenterConnectionDetails(credentials.host, credentials.username, credentials.password))
        virtual_switch_to_machine_connector = VirtualSwitchToMachineConnector(pyVmomiService(SmartConnect, Disconnect),
                                                                              SynchronousTaskWaiter(),
                                                                              resource_connection_details_retriever)

        vlan_id = 'VLAN 1-DVUplinks-9203'
        virtual_machine_name = 'boris1'
        virtual_machine_path = 'Boris\\boris1'
        dv_switch_path = 'QualiSB'
        dv_switch_name = 'dvSwitch'
        dv_port_name = 'boris_group1'
        port_group = virtual_switch_to_machine_connector.connect(virtual_machine_name, dv_switch_path, dv_switch_name,
                                                                 dv_port_name)

        print port_group
