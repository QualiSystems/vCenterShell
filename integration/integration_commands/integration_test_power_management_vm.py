from unittest import TestCase

from pyVim.connect import SmartConnect, Disconnect
from cloudshell.cp.vcenter.commands.power_manager_vm import VirtualMachinePowerManagementCommand

from cloudshell.cp.vcenter.common.logger.service import LoggingService
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.common.vcenter.task_waiter import task_waiter
from tests.utils.testing_credentials import TestCredentials


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
