import unittest
import mock
from mock import Mock, MagicMock, create_autospec
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))
from pycommon.cloudshellDataRetrieverService import *

class test_cloudshellDataRetrieverService(unittest.TestCase):
    def setUp(self):
        self.csRetrieverService = cloudshellDataRetrieverService()

    def tearDown(self):
        pass

    def test_getVCenterTemplateAttributeData(self):
        # Arrange
        attributes = {"vCenter Template": "vCenter/Alex/test"}
        resource_attributes = Mock(attributes=attributes)

        # Act
        result = self.csRetrieverService.getVCenterTemplateAttributeData(resource_attributes);

        # Assert
        self.assertEquals(result["vCenter_resource_name"], "vCenter")
        self.assertEqual(result["vm_folder"], "Alex")
        self.assertEqual(result["template_name"], "test")

    def test_getPowerStateAttributeData_Value_Is_True(self):
        # Arrange
        attributes = {"VM Power State": "True"}
        resource_attributes = Mock(attributes=attributes)

        # Act
        result = self.csRetrieverService.getPowerStateAttributeData(resource_attributes);

        # Assert
        self.assertEquals(result, True)

    def test_getPowerStateAttributeData_Value_Is_False(self):
        # Arrange
        attributes = {"VM Power State": "False"}
        resource_attributes = Mock(attributes=attributes)

        # Act
        result = self.csRetrieverService.getPowerStateAttributeData(resource_attributes);

        # Assert
        self.assertEquals(result, False)

    def test_getVMClusterAttributeData(self):
        # Arrange
        attributes = {"VM Cluster": "cluster1/resourcepool1"}
        resource_attributes = Mock(attributes=attributes)

        # Act
        result = self.csRetrieverService.getVMClusterAttributeData(resource_attributes);

        # Assert
        self.assertEquals(result["cluster_name"], "cluster1")
        self.assertEquals(result["resource_pool"], "resourcepool1")

    def test_getVMClusterAttributeData_Empty_Attribute(self):
        # Arrange
        attributes = {"VM Cluster": ""}
        resource_attributes = Mock(attributes=attributes)

        # Act
        result = self.csRetrieverService.getVMClusterAttributeData(resource_attributes);

        # Assert
        self.assertEquals(result["cluster_name"], None)
        self.assertEquals(result["resource_pool"], None)

    
    def test_getVMStorageAttributeData(self):
        # Arrange
        attributes = {"VM Storage": "my storage"}
        resource_attributes = Mock(attributes=attributes)

        # Act
        datastore_name = self.csRetrieverService.getVMStorageAttributeData(resource_attributes);

        # Assert
        self.assertEquals(datastore_name, "my storage")

    def test_getVMStorageAttributeData_Empty_Attribute(self):
        # Arrange
        attributes = {"VM Storage": ""}
        resource_attributes = Mock(attributes=attributes)

        # Act
        datastore_name = self.csRetrieverService.getVMStorageAttributeData(resource_attributes);

        # Arrange
        self.assertEquals(datastore_name, None)

    def test_getVCenterConnectionDetails(self):
        # Arrange
        password = "pass1"
        session = Mock()
        session.DecryptPassword = Mock(return_value=Mock(Value=password))

        attributes = [Mock(Name="User",Value="user1"),Mock(Name="Password",Value=password)]
        vCenter_resource_details = Mock(ResourceAttributes=attributes, Address="vCenterIP")

         # Act
        connDetails = self.csRetrieverService.getVCenterConnectionDetails(session, vCenter_resource_details);

        # Assert
        self.assertEquals(connDetails["user"], "user1")
        self.assertEquals(connDetails["password"], "pass1")
        self.assertEquals(connDetails["vCenter_url"], "vCenterIP")

    def test_getVCenterInventoryPathAttributeData(self):
        # Arrange
        attributes = {"vCenter Inventory Path": "vCenter/Alex"}
        resource_attributes = Mock(attributes=attributes)

        # Act
        result = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_attributes);

        # Assert
        self.assertEquals(result["vCenter_resource_name"], "vCenter")
        self.assertEqual(result["vm_folder"], "Alex")



