from unittest import TestCase
from mock import create_autospec
from qualipy.api.cloudshell_api import ResourceInfo
from qualipy.scripts.cloudshell_scripts_helpers import ResourceContextDetails

from common.model_factory import ResourceModelParser


class TestResourceModelParser(TestCase):
    def test_parse_resource_model(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceContextDetails)

        resource_info.model = 'VLAN Auto'
        resource_info.attrib = {'Access Mode': 'Trunk', 'VLAN Id': '123', 'Allocation Ranges': '2-4094',
                                'Virtual Network': '', 'Isolation Level': 'Exclusive'}
        resource_model = resource_model_parser.convert_to_resource_model(resource_info)

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

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info)

    def test_parse_resource_model_class_does_not_exist(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceContextDetails)

        resource_info.model = 'NOT EXISTS'

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info)

    def test_parse_resource_info_model(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceInfo)

        resource_info.ResourceModelName = 'VLAN Auto'
        resource_info.ResourceAttributes = {'Access Mode': 'Trunk', 'VLAN Id': '123', 'Allocation Ranges': '2-4094',
                                            'Virtual Network': '', 'Isolation Level': 'Exclusive'}
        resource_model = resource_model_parser.convert_to_resource_model(resource_info)

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

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info)

    def test_parse_resource_info_model_class_does_not_exist(self):
        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceInfo)

        resource_info.ResourceModelName = 'NOT EXISTS'

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info)
