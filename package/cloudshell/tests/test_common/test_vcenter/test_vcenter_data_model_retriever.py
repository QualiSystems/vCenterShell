import unittest

from mock import Mock, create_autospec
from cloudshell.cp.vcenter.models.QualiDriverModels import ResourceContextDetails

from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.cp.vcenter.common.vcenter.data_model_retriever import VCenterDataModelRetriever


class TestVCenterDataModelRetriever(unittest.TestCase):

    def test_get_vcenter_data_model(self):
        # Arrange
        data_model_retriever = VCenterDataModelRetriever(ResourceModelParser())
        api = Mock()
        vcenter_resource = create_autospec(ResourceContextDetails)

        vcenter_resource.model = 'VMWare vCenter'
        vcenter_resource.attrib = {'user': 'uzer',
                                   'password': 'pwd',
                                   'default_dvswitch': '',
                                   'holding_network': '',
                                   'vm_cluster': '',
                                   'vm_resource_pool': '',
                                   'vm_storage': '',
                                   'vm_location': '',
                                   'shutdown_method': '',
                                   'ovf_tool_path': '',
                                   'execution_server_selector': '',
                                   'reserved_networks': '',
                                   'default_datacenter': ''}

        api.GetResourceDetails = Mock(return_value=vcenter_resource)

        # Act
        vcenter_data_model = data_model_retriever.get_vcenter_data_model(api, 'VMWare Center')

        # Assert
        self.assertEqual(vcenter_data_model.user, 'uzer')

    def test_get_vcenter_data_model_empty_vcenter_name(self):
        # Arrange
        data_model_retriever = VCenterDataModelRetriever(ResourceModelParser())
        api = Mock()
        vcenter_resource = create_autospec(ResourceContextDetails)

        vcenter_resource.model = 'VMWare vCenter'
        vcenter_resource.attrib = {'user': 'uzer',
                                   'password': 'pwd',
                                   'default_dvswitch': '',
                                   'holding_network': '',
                                   'vm_cluster': '',
                                   'vm_resource_pool': '',
                                   'vm_storage': '',
                                   'vm_location': '',
                                   'shutdown_method': '',
                                   'ovf_tool_path': '',
                                   'execution_server_selector': '',
                                   'reserved_networks': '',
                                   'default_datacenter': ''}

        api.GetResourceDetails = Mock(return_value=vcenter_resource)

        # Act + Assert
        self.assertRaises(ValueError, data_model_retriever.get_vcenter_data_model,api, '')
