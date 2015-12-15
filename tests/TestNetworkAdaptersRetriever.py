import os.path
import sys
import unittest

from mock import Mock, create_autospec
from pyVmomi import vim


sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell'))
from vCenterShell.models.VCenterConnectionDetails import *
from vCenterShell.commands.NetworkAdaptersRetrieverCommand import *


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

        csRetrieverService = Mock()
        csRetrieverService.getVCenterInventoryPathAttributeData = Mock(
            return_value={'vCenter_resource_name': 'Resource Name'})

        helpers.get_resource_context_details = Mock(return_value={})

        connDetails = create_autospec(VCenterConnectionDetails)
        connDetails.host = 'host'
        connDetails.user = 'user'
        connDetails.password = 'pwd'
        connDetails.port = 443

        resourceConnectionDetailsRetriever = Mock()
        resourceConnectionDetailsRetriever.getConnectionDetails = Mock(return_value=connDetails)

        switchRetriever = NetworkAdaptersRetrieverCommand(pvService, csRetrieverService, resourceConnectionDetailsRetriever)
        nics = switchRetriever.execute()

        self.assertEqual(nics[0].networkLabel, 'network1')
        self.assertEqual(nics[0].macAddress, 'AA-BB')
        self.assertEqual(nics[0].connected, 'True')
        self.assertEqual(nics[0].connectAtPowerOn, 'True')


if __name__ == '__main__':
    unittest.main()
