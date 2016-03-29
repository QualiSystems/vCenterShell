from unittest import TestCase

from cloudshell.api.cloudshell_api import ResourceInfo, ResourceAttribute
from mock import create_autospec
from cloudshell.helpers.scripts.cloudshell_scripts_helpers import ResourceContextDetails

from cloudshell.cp.vcenter.models.VLANAutoResourceModel import VLANAutoResourceModel

from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser


class TestResourceModelParser(TestCase):
    def test_parse_resource_model(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceContextDetails)

        resource_info.model = 'VLAN Auto'
        resource_info.attrib = {'Access Mode': 'Trunk', 'VLAN ID': '123', 'Allocation Ranges': '2-4094',
                                'Virtual Network': '', 'Isolation Level': 'Exclusive'}
        resource_model = resource_model_parser.convert_to_resource_model(resource_info, None)

        self.assertEqual(resource_model.access_mode, 'Trunk')
        self.assertEqual(resource_model.vlan_id, '123')
        self.assertEqual(resource_model.isolation_level, 'Exclusive')
        self.assertEqual(resource_model.allocation_ranges, '2-4094')
        self.assertEqual(resource_model.virtual_network, '')
        self.assertEqual(resource_model.virtual_network_attribute, 'Virtual Network')

    def test_parse_resource_model_missing_attribute(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceContextDetails)

        # ResourceInfo({'Name': '', 'ResourceModelName': 'Simple'})
        resource_info.model = 'VLAN Auto'
        resource_info.attrib = {'Access Mode': 'Trunk'}

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info, None)

    def test_parse_resource_model_class_does_not_exist(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceContextDetails)

        resource_info.model = 'NOT EXISTS'

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info, None)

    def test_parse_resource_info_model_with_specified_type(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceInfo)

        resource_info.ResourceModelName = None
        resource_info.ResourceAttributes = {'Access Mode': 'Trunk', 'VLAN ID': '123', 'Allocation Ranges': '2-4094',
                                            'Virtual Network': '', 'Isolation Level': 'Exclusive'}
        resource_model = resource_model_parser.convert_to_resource_model(resource_info,
                                                                         VLANAutoResourceModel)

        self.assertEqual(resource_model.access_mode, 'Trunk')
        self.assertEqual(resource_model.vlan_id, '123')
        self.assertEqual(resource_model.isolation_level, 'Exclusive')
        self.assertEqual(resource_model.allocation_ranges, '2-4094')
        self.assertEqual(resource_model.virtual_network, '')
        self.assertEqual(resource_model.virtual_network_attribute, 'Virtual Network')

    def test_parse_resource_info_model_with_specified_type_by_string(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceInfo)

        resource_info.ResourceModelName = None
        resource_info.ResourceAttributes = {'Access Mode': 'Trunk', 'VLAN ID': '123', 'Allocation Ranges': '2-4094',
                                            'Virtual Network': '', 'Isolation Level': 'Exclusive'}

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info,
                          'VLANAutoResourceModel')

    def test_parse_resource_info_model(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceInfo)

        resource_info.ResourceModelName = 'VLAN Auto'
        resource_info.ResourceAttributes = {'Access Mode': 'Trunk', 'VLAN Id': '123', 'Allocation Ranges': '2-4094',
                                            'Virtual Network': '', 'Isolation Level': 'Exclusive'}
        resource_model = resource_model_parser.convert_to_resource_model(resource_info, None)

        self.assertEqual(resource_model.access_mode, 'Trunk')
        self.assertEqual(resource_model.vlan_id, '123')
        self.assertEqual(resource_model.isolation_level, 'Exclusive')
        self.assertEqual(resource_model.allocation_ranges, '2-4094')
        self.assertEqual(resource_model.virtual_network, '')
        self.assertEqual(resource_model.virtual_network_attribute, 'Virtual Network')

    def test_parse_resource__info_model_missing_attribute(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceInfo)

        resource_info.ResourceModelName = 'VLAN Auto'
        resource_info.ResourceAttributes = {'Access Mode': 'Trunk'}

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info, None)

    def test_parse_resource_info_model_class_does_not_exist(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceInfo)

        resource_info.ResourceModelName = 'NOT EXISTS'

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info, None)

    def test_parse_response_info(self):
        resource_info = create_autospec(ResourceInfo)
        resource_info.ResourceModelName = 'Generic Deployed App'

        vm_uuid_attribute = create_autospec(ResourceAttribute)
        vm_uuid_attribute.Name = 'VM_UUID'
        vm_uuid_attribute.Value = '422258cd-8b76-e375-8c3b-8e1bf86a4713'

        cloud_provider_attribute = create_autospec(ResourceAttribute)
        cloud_provider_attribute.Name = 'Cloud Provider'
        cloud_provider_attribute.Value = 'vCenter'

        resource_info.ResourceAttributes = [vm_uuid_attribute, cloud_provider_attribute]

        resource_model_parser = ResourceModelParser()
        resource_model = resource_model_parser.convert_to_resource_model(resource_info, None)

        self.assertEqual(resource_model.vm_uuid, '422258cd-8b76-e375-8c3b-8e1bf86a4713')
