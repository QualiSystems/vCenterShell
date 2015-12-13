import unittest
from mock import Mock, MagicMock, create_autospec, mock_open, patch

import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from dvSwitchDataRetriever import dvSwitchDataRetriever
from pycommon.common_pyvmomi import pyVmomiService
from testCredentials import *

class test_dvSwitchDataRetriever(unittest.TestCase):

    # Integration test, Ignored it on CI
    def integrationTest_RetrieveDvSwitchData_integrationTest(self):
        cred = testCredentials()
        switchRetriever = dvSwitchDataRetriever(pyVmomiService(SmartConnect, Disconnect))
        switch = switchRetriever.RetrieveDvSwitchData(cred.host, cred.username, cred.password, 443, 'bla')

        self.assertEqual(True, True)

    def test_RetrieveDvSwitchData_unitTest(self):
        content = Mock()
        connection = create_autospec(spec = vim.ServiceInstance)
        connection.RetrieveContent = Mock(return_value = content)

        vNic = create_autospec(spec = vim.vm.device.VirtualEthernetCard)
        vNic.deviceInfo = Mock()
        vNic.deviceInfo.summary = 'network1'
        vNic.macAddress = 'AA-BB'
        vNic.connectable = Mock()
        vNic.connectable.connected = 'True'
        vNic.connectable.startConnected = 'True'

        vmMachine = Mock()
        vmMachine.config.hardware.device = [vNic]

        mockPyVmomiService = Mock()
        mockPyVmomiService.connect = Mock(return_value = connection)
        mockPyVmomiService.get_obj = Mock(return_value = vmMachine)

        switchRetriever = dvSwitchDataRetriever(mockPyVmomiService)
        nics = switchRetriever.RetrieveDvSwitchData('host', 'user', 'pwd', 443, 'vmName')

        self.assertEqual(nics[0].networkLabel, 'network1')
        self.assertEqual(nics[0].macAddress, 'AA-BB')
        self.assertEqual(nics[0].connected, 'True')
        self.assertEqual(nics[0].connectAtPowerOn, 'True')

if __name__ == '__main__':
    unittest.main()
