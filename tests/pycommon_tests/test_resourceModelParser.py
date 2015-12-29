from unittest import TestCase
from mock import create_autospec
from qualipy.api.cloudshell_api import ResourceInfo

from pycommon.ResourceModelParser import ResourceModelParser


class TestResourceModelParser(TestCase):
    def test_parse_resource_model(self):

        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceInfo)

        # ResourceInfo({'Name': '', 'ResourceModelName': 'Simple'})
        resource_info.ResourceModelName = 'VLAN'
        resource_info.attrib = {'Access Mode': 'Trunk', 'VLAN ID': '123'}
        resource_model = resource_model_parser.convert_to_resource_model(resource_info)

        self.assertEqual(resource_model.access_mode, 'Trunk')
        self.assertEqual(resource_model.vlan_id, '123')

    def test_parse_resource_model_missing_attribute(self):

        resource_model_parser = ResourceModelParser()

        resource_info = create_autospec(ResourceInfo)

        # ResourceInfo({'Name': '', 'ResourceModelName': 'Simple'})
        resource_info.ResourceModelName = 'VLAN'
        resource_info.attrib = {'Access Mode': 'Trunk'}

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, resource_info)

