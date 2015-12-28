from unittest import TestCase
from mock import Mock
from pyVim.connect import SmartConnect, Disconnect
from models.VCenterConnectionDetails import VCenterConnectionDetails
from pycommon import SynchronousTaskWaiter
from pycommon.logging_service import LoggingService
from pycommon.pyVmomiService import pyVmomiService
from tests.testCredentials import TestCredentials
from vCenterShell.commands.VirtualSwitchToMachineDisconnectCommand import VirtualSwitchToMachineDisconnectCommand


class VirtualSwitchToMachineCommandIntegrationTest(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def integration_test_delete_all(self):
        # arrange
        cred = TestCredentials()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        si = pv_service.connect(cred.host, cred.username, cred.password)

        resource_connection_details_retriever = Mock()
        credentials = TestCredentials()
        resource_connection_details_retriever.connection_details = Mock(
            return_value=VCenterConnectionDetails(credentials.host, credentials.username, credentials.password))

        virtual_switch_to_machine_connector = \
            VirtualSwitchToMachineDisconnectCommand(pv_service,
                                                    resource_connection_details_retriever,
                                                    SynchronousTaskWaiter.SynchronousTaskWaiter())
        uuid = pv_service.find_vm_by_name(si, 'QualiSB/Raz', 'New Virtual Machine').config.uuid

        virtual_switch_to_machine_connector.disconnect_all('name of the vCenter',
                                                           uuid)

    def integration_test_delete_specific(self):
        # arrange
        cred = TestCredentials()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        si = pv_service.connect(cred.host, cred.username, cred.password)

        resource_connection_details_retriever = Mock()
        credentials = TestCredentials()
        resource_connection_details_retriever.connection_details = Mock(
            return_value=VCenterConnectionDetails(credentials.host, credentials.username, credentials.password))

        virtual_switch_to_machine_connector = \
            VirtualSwitchToMachineDisconnectCommand(pv_service,
                                                    resource_connection_details_retriever,
                                                    SynchronousTaskWaiter.SynchronousTaskWaiter())
        uuid = pv_service.find_vm_by_name(si, 'QualiSB/Raz/', '2').config.uuid

        virtual_switch_to_machine_connector.disconnect('name of the vCenter',
                                                       uuid,
                                                       'QS_TMP_PORTGROUP')
