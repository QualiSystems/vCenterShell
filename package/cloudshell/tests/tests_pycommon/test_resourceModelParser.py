from unittest import TestCase

from cloudshell.api.cloudshell_api import ResourceInfo, ResourceAttribute
from mock import create_autospec
from cloudshell.helpers.scripts.cloudshell_scripts_helpers import ResourceContextDetails

from cloudshell.cp.vcenter.models.GenericDeployedAppResourceModel import GenericDeployedAppResourceModel
from cloudshell.cp.vcenter.models.VLANAutoResourceModel import VLANAutoResourceModel

from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser


class TestResourceModelParser(TestCase):

    def test_parse_resource_model_missing_attribute(self):
        resource_model_parser = ResourceModelParser()

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, {'Access Mode': 'Trunk'}, 'VLANAutoResourceModel')

    def test_parse_resource_model_class_does_not_exist(self):
        resource_model_parser = ResourceModelParser()

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, {}, None)

    def test_parse_resource_info_model_with_specified_type(self):
        resource_model_parser = ResourceModelParser()

        attributes = {'Access Mode': 'Trunk', 'VLAN ID': '123', 'Allocation Ranges': '2-4094',
                                            'Virtual Network': '', 'Isolation Level': 'Exclusive'}
        resource_model = resource_model_parser.convert_to_resource_model(attributes, VLANAutoResourceModel)

        self.assertEqual(resource_model.access_mode, 'Trunk')
        self.assertEqual(resource_model.vlan_id, '123')
        self.assertEqual(resource_model.isolation_level, 'Exclusive')
        self.assertEqual(resource_model.allocation_ranges, '2-4094')
        self.assertEqual(resource_model.virtual_network, '')
        self.assertEqual(resource_model.virtual_network_attribute, 'Virtual Network')

    def test_parse_resource_info_model_with_specified_type_by_string(self):
        resource_model_parser = ResourceModelParser()

        attributes = {'Access Mode': 'Trunk', 'VLAN ID': '123', 'Allocation Ranges': '2-4094',
                                            'Virtual Network': '', 'Isolation Level': 'Exclusive'}

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, attributes, 'VLANAutoResourceModel')

    def test_parse_resource_info_model(self):
        resource_model_parser = ResourceModelParser()

        attributes = {'Access Mode': 'Trunk', 'VLAN Id': '123', 'Allocation Ranges': '2-4094',
                                            'Virtual Network': '', 'Isolation Level': 'Exclusive'}
        resource_model = resource_model_parser.convert_to_resource_model(attributes, VLANAutoResourceModel)

        self.assertEqual(resource_model.access_mode, 'Trunk')
        self.assertEqual(resource_model.vlan_id, '123')
        self.assertEqual(resource_model.isolation_level, 'Exclusive')
        self.assertEqual(resource_model.allocation_ranges, '2-4094')
        self.assertEqual(resource_model.virtual_network, '')
        self.assertEqual(resource_model.virtual_network_attribute, 'Virtual Network')

    def test_parse_resource__info_model_missing_attribute(self):
        resource_model_parser = ResourceModelParser()

        attributes = {'Access Mode': 'Trunk'}

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, attributes, VLANAutoResourceModel)

    def test_parse_resource_info_model_class_does_not_exist(self):
        resource_model_parser = ResourceModelParser()

        self.assertRaises(ValueError, resource_model_parser.convert_to_resource_model, {}, None)

    def test_parse_response_info(self):
        resource_model_parser = ResourceModelParser()

        attributes = {'VM_UUID': '422258cd-8b76-e375-8c3b-8e1bf86a4713', 'Cloud Provider':'vCenter' }

        resource_model = resource_model_parser.convert_to_resource_model(attributes, GenericDeployedAppResourceModel)

        self.assertEqual(resource_model.vm_uuid, '422258cd-8b76-e375-8c3b-8e1bf86a4713')
