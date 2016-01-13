from unittest import TestCase

from pyVim.connect import SmartConnect, Disconnect

from common.vcenter.vmomi_service import pyVmomiService
from tests.utils.testing_credentials import TestCredentials
from vCenterShell.network.vnic.vnic_updater import VnicUpdater
import qualipy.scripts.cloudshell_scripts_helpers as helpers
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers

class VirtualSwitchToMachineCommandIntegrationTest(TestCase):

    def integration_test_update_vnics(self):

        dev_helpers.attach_to_cloudshell_as("admin", "admin", "Global", "4571b4fe-be5d-4556-aed9-54c91b9b1bb1")
        details = helpers.get_reservation_context_details()
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)

        vnic_updater = VnicUpdater(helpers)
