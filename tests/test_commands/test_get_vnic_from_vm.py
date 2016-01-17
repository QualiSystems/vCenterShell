import os.path
import sys
import unittest

import qualipy.scripts.cloudshell_scripts_helpers as helpers
from mock import Mock, create_autospec
from pyVmomi import vim

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell'))
from models.VCenterConnectionDetails import *
from vCenterShell.commands.get_vnic_from_vm import NetworkAdaptersRetrieverCommand, ConnectionException


class TestNetworkAdaptersRetriever(unittest.TestCase):

    def test_TestNetworkAdaptersRetriever(self):
        content = Mock()
        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock(return_value=content)

        vNic = create_autospec(spec=vim.vm.device.VirtualEthernetCard)
        vNic.deviceInfo = Mock()
        vNic.deviceInfo.summary = 'network1'
        vNic.macAddress = 'AA-BB'
        vNic.connectable = Mock()
        vNic.connectable.connected = 'True'
        vNic.connectable.startConnected = 'True'

        vmMachine = Mock()
        vmMachine.config.hardware.device = [vNic]

        pvService = Mock()
        pvService.connect = Mock(return_value=si)
        pvService.get_obj = Mock(return_value=vmMachine)
        pvService.find_network_by_name = Mock(return_value=vmMachine)

        switchRetriever = NetworkAdaptersRetrieverCommand(pvService)
        nics = switchRetriever.retrieve(si, "some path", "network name")

        self.assertEqual(nics[0].networkLabel, 'network1')
        self.assertEqual(nics[0].macAddress, 'AA-BB')
        self.assertEqual(nics[0].connected, 'True')
        self.assertEqual(nics[0].connectAtPowerOn, 'True')

if __name__ == '__main__':
    unittest.main()
