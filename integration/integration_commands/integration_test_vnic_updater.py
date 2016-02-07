import os
from unittest import TestCase

from pyVim.connect import SmartConnect, Disconnect
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers
from common.vcenter.vmomi_service import pyVmomiService
from tests.utils.testing_credentials import TestCredentials
import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim


class VirtualSwitchToMachineCommandIntegrationTest(TestCase):

    def integration_test(self):

        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)
        vm = py_vmomi_service.find_vm_by_name(si, 'QualiSB/Alex', 'Ubuntu_a287f573')

        os.environ['VM_UUID'] = vm.config.uuid
        os.environ['VLAN_ID'] = '25'
        os.environ['VLAN_SPEC_TYPE'] = 'Access'

        bootstrapper = Bootstrapper()
        executer_service = bootstrapper.get_command_executer_service()
        executer_service.connect()

    def integration_test_update_vnics(self):


        dev_helpers.attach_to_cloudshell_as("admin", "admin", "Global", "1205e711-edf7-4b12-8a5e-e0ff53768ce7")
        details = helpers.get_reservation_context_details()
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)
        vm = py_vmomi_service.find_vm_by_name(si, 'QualiSB/Alex', 'Ubuntu_a287f573')

        nics = [x for x in vm.config.hardware.device
                if isinstance(x, vim.vm.device.VirtualEthernetCard)]

        for nic in nics:
            network_name = nic.backing.network.name
            mac_address = nic.macAddress

            print network_name + mac_address

    def integration_test_update_vnics(self):

        dev_helpers.attach_to_cloudshell_as("admin", "admin", "Global", "8d36098c-6dd0-4d47-8ad8-b159191e3f63")
        details = helpers.get_reservation_context_details()
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)
        vm = py_vmomi_service.find_by_uuid(si, '4222941e-a02d-dc78-80f6-44b88e0cb24f')

        nics = [x for x in vm.config.hardware.device
                if isinstance(x, vim.vm.device.VirtualEthernetCard)]

        for nic in nics:
            network_name = nic.backing.network.name
            mac_address = nic.macAddress

            print network_name + mac_address

    def test_test(self):

        dev_helpers.attach_to_cloudshell_as("admin", "admin", "Global", "8d36098c-6dd0-4d47-8ad8-b159191e3f63")
        details = helpers.get_reservation_context_details()
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)
        vm = py_vmomi_service.find_by_uuid(si, '4222941e-a02d-dc78-80f6-44b88e0cb24f')
        network = py_vmomi_service.get_network_by_mac_address(vm, '00:50:56:a2:06:87')

        print network.name






