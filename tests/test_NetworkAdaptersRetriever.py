import unittest
from mock import Mock, MagicMock, create_autospec, mock_open, patch
from pyVmomi import vim

import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))
from pycommon.cloudshellDataRetrieverService import *
from models.VCenterConnectionDetails import *
from commands.NetworkAdaptersRetriever import *
from models.VirtualNic import VirtualNic

class test_NetworkAdaptersRetriever(unittest.TestCase):

    # Integration test, Ignored it on CI
    def integrationTest_RetrieveDvSwitchData_integrationTest(self):
        cred = TestCredentials()
        switchRetriever = NetworkAdaptersRetriever(pyVmomiService(SmartConnect, Disconnect))
        switch = switchRetriever.Execute()

        self.assertEqual(True, True)

    def test_RetrieveDvSwitchData_unitTest(self):
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

        csRetrieverService = Mock()
        csRetrieverService.getVCenterInventoryPathAttributeData = Mock(return_value={'vCenter_resource_name': 'Resource Name'})

        helpers.get_resource_context_details = Mock(return_value={})

        connDetails = create_autospec(VCenterConnectionDetails)
        connDetails.host = 'host'
        connDetails.user = 'user'
        connDetails.password = 'pwd'
        connDetails.port = 443

        resourceConnectionDetailsRetriever = Mock()
        resourceConnectionDetailsRetriever.getConnectionDetails = Mock(return_value=connDetails)

        switchRetriever = NetworkAdaptersRetriever(pvService, csRetrieverService, resourceConnectionDetailsRetriever)
        nics = switchRetriever.execute()

        self.assertEqual(nics[0].networkLabel, 'network1')
        self.assertEqual(nics[0].macAddress, 'AA-BB')
        self.assertEqual(nics[0].connected, 'True')
        self.assertEqual(nics[0].connectAtPowerOn, 'True')

if __name__ == '__main__':
    unittest.main()
