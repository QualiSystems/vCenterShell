from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from pycommon.common_pyvmomi import pyVmomiService
import unittest
import mock
from mock import Mock, MagicMock, create_autospec, mock_open, patch

class test_common_pyvmomi(unittest.TestCase):
    def setUp(self):
        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock()
        si.content = create_autospec(spec=vim.ServiceInstanceContent())
        
        mockObj= Mock()
        mockObj.SmartConnect = Mock(return_value=si)
        mockObj.Disconnect = Mock()
        
        self.pvService = pyVmomiService(mockObj.SmartConnect,mockObj.Disconnect)

    def tearDown(self):
        pass

    #def test_can_connect_successfully(self):
    #    #arrange
    #    si = self.pvService.connect("vCenter", "user", "pass")
    #    #assert
    #    result = "1"
    #    self.assertEqual(result,"1")



if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)