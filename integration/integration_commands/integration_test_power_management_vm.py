from unittest import TestCase

from vCenterShell.common.logger.service import LoggingService
from pyVim.connect import SmartConnect, Disconnect

from tests.utils.testing_credentials import TestCredentials
from vCenterShell.commands.power_manager_vm import VirtualMachinePowerManagementCommand
from vCenterShell.common.vcenter import pyVmomiService
from vCenterShell.common.vcenter import task_waiter


class VirtualMachinePowerManagementCommandIntegrationTest(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def test_power_management(self):
        # arrange
        cred = TestCredentials()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        si = pv_service.connect(cred.host, cred.username, cred.password)

        uuid = pv_service.find_vm_by_name(si, 'QualiSB/Raz', '2').config.uuid
        power_manager = VirtualMachinePowerManagementCommand(pv_service,
                                                             task_waiter.SynchronousTaskWaiter())

        power_manager.power_on(si, uuid)
        power_manager.power_off(si, uuid)
