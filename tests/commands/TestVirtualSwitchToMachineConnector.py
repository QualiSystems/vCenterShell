from unittest import TestCase
from mock import Mock
from pyVim.connect import SmartConnect, Disconnect
from models.VCenterConnectionDetails import VCenterConnectionDetails
from pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter
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

        vlan_id = 'VM Network'
        virtual_machine_name = 'boris1'
        virtual_machine_path = 'Boris\\boris1'
        network_name = 'VM Network'
        network_path = 'QualiTest'
        datacenter_name = 'QualiSB'
        cluster_path = 'QualiSB\\a'
        cluster_name = 'QualiSB Cluster'
        virtual_switch_to_machine_connector.connect(vlan_id, virtual_machine_name, virtual_machine_path, network_name,
                                                    network_path, datacenter_name, cluster_path, cluster_name)
