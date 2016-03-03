import os.path
import sys
import unittest

from mock import Mock

from common.cloud_shell.data_retriever import CloudshellDataRetrieverService

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))

class test_cloudshellDataRetrieverService(unittest.TestCase):
    def setUp(self):
        self.csRetrieverService = CloudshellDataRetrieverService()

    def test_getVCenterConnectionDetails(self):
        # Arrange
        password = "pass1"
        session = Mock()
        session.DecryptPassword = Mock(return_value=Mock(Value=password))

        attributes = {"User": "user1", "Password": password}
        vCenter_resource_details = Mock()
        vCenter_resource_details.attributes = attributes
        vCenter_resource_details.address = 'vCenterIP'


         # Act
        conn_details = self.csRetrieverService.getVCenterConnectionDetails(session, vCenter_resource_details)

        # Assert
        self.assertEquals(conn_details.username, "user1")
        self.assertEquals(conn_details.password, "pass1")
        self.assertEquals(conn_details.host, "vCenterIP")




