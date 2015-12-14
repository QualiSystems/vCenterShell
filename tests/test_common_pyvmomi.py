import os.path
import sys
import unittest

from mock import Mock, create_autospec
from pyVmomi import vim

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell'))

from vCenterShell.pycommon.pyVmomiService import pyVmomiService


class ignore_test_common_pyvmomi(unittest.TestCase):
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