from unittest import TestCase

from mock import Mock
from pyVim.connect import SmartConnect, Disconnect

from common.logger.service import LoggingService
from common.vcenter import task_waiter
from common.vcenter.vmomi_service import pyVmomiService
from models.VCenterConnectionDetails import VCenterConnectionDetails
from tests.testCredentials import TestCredentials
from vCenterShell.commands.power_manager_vm import VirtualMachinePowerManagementCommand


class VirtualMachinePowerManagementCommandIntegrationTest(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def test_power_on(self):
        # arrange
        cred = TestCredentials()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        si = pv_service.connect(cred.host, cred.username, cred.password)
        resource_att = Mock()
        qualipy_helpers = Mock()
        resource_connection_details_retriever = Mock()

        inventory_path_data = {'vCenter_resource_name': Mock()}
        qualipy_helpers.get_resource_context_details = Mock(return_value=resource_att)
        resource_connection_details_retriever.getVCenterInventoryPathAttributeData = \
            Mock(return_value=inventory_path_data)

        credentials = TestCredentials()
        resource_connection_details_retriever.connection_details = Mock(
            return_value=VCenterConnectionDetails(credentials.host, credentials.username, credentials.password))

        uuid = pv_service.find_vm_by_name(si, 'QualiSB/Raz', '2').config.uuid
        power_manager = VirtualMachinePowerManagementCommand(pv_service,
                                                             resource_connection_details_retriever,
                                                             task_waiter.SynchronousTaskWaiter(),
                                                             qualipy_helpers)

        power_manager.power_on(uuid)

    def test_power_off(self):
        # arrange
        cred = TestCredentials()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        si = pv_service.connect(cred.host, cred.username, cred.password)
        resource_att = Mock()
        qualipy_helpers = Mock()
        resource_connection_details_retriever = Mock()

        inventory_path_data = {'vCenter_resource_name': Mock()}
        qualipy_helpers.get_resource_context_details = Mock(return_value=resource_att)
        resource_connection_details_retriever.getVCenterInventoryPathAttributeData = \
            Mock(return_value=inventory_path_data)

        credentials = TestCredentials()
        resource_connection_details_retriever.connection_details = Mock(
            return_value=VCenterConnectionDetails(credentials.host, credentials.username, credentials.password))

        uuid = pv_service.find_vm_by_name(si, 'QualiSB/Raz', '2').config.uuid
        power_manager = VirtualMachinePowerManagementCommand(pv_service,
                                                             resource_connection_details_retriever,
                                                             task_waiter.SynchronousTaskWaiter(),
                                                             Mock())

        power_manager.power_off(uuid)
