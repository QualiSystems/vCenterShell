import os
import sys
import xml.etree.ElementTree as ET
from os import listdir
from unittest import TestCase

from common.model_factory import ResourceModelParser
from common.logger.service import LoggingService

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell'))


class TestDataModel(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def test_resource_models(self):
        ns = {'default': 'http://schemas.qualisystems.com/ResourceManagement/DataModelSchema.xsd'}
        datamodel_path = os.path.join(os.path.dirname(__file__), '../../vCenterShellPackage/DataModel/datamodel.xml')
        tree = ET.parse(datamodel_path)
        root = tree.getroot()
        resource_models = root.findall('.//default:ResourceModel', ns)
        self.assertGreater(len(resource_models), 0)
        validation_errors = []
        for resource_model in resource_models:
            model_name = ResourceModelParser().get_resource_model_class_name(resource_model.attrib['Name'])

            try:
                klass = ResourceModelParser().get_class('models.' + model_name)
            except ValueError as value_error:
                validation_errors.append('Failed to parse Model Name {0} with error {1}.'.format(model_name, value_error.message))
                continue

            attribute_names = self.get_model_attributes(ns, resource_model)

            for attribute_name in attribute_names:
                if not hasattr(klass, attribute_name):
                    validation_errors.append('attribute {0} is missing on class {1}'.format(attribute_name, model_name))

        for validation_error in validation_errors:
            print validation_error

        self.assertSequenceEqual(validation_errors, [])

    def test_app_templates(self):
        xml_files = self.get_app_templates_xml_files()
        for xml_file in xml_files:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            deployment_nodes = root.findall('.//DeploymentService')
            validation_errors = []
            for deployment_node in deployment_nodes:
                resource_model_name = self.get_class_name_from_model_node(deployment_node)
                try:
                    klass = ResourceModelParser().get_class('models.' + resource_model_name)
                except ValueError as value_error:
                    validation_errors.append(value_error.message)
                    continue

                attribute_names = self.get_template_attributes(deployment_node)

                for attribute_name in attribute_names:
                    if not hasattr(klass, attribute_name):
                        validation_errors.append('attribute {0} is missing on class {1}'.format(attribute_name,
                                                                                                resource_model_name))

        for validation_error in validation_errors:
            print validation_error

        self.assertSequenceEqual(validation_errors, [])

    def get_app_templates_xml_files(self):
        app_templates_path = os.path.join(os.path.dirname(__file__), '../../vCenterShellPackage/App Templates/')
        xml_files = [os.path.join(app_templates_path, f)
                     for f in listdir(app_templates_path)
                     if os.path.splitext(f)[1] == '.xml']
        return xml_files

    def get_model_attributes(self, ns, resource_model):
        attribute_nodes = resource_model.findall('default:AttachedAttributes/default:AttachedAttribute', ns)
        attribute_names = [self.get_attribute_name_from_attribute_node(attribute_node)
                           for attribute_node
                           in attribute_nodes]
        return attribute_names

    def get_template_attributes(self, resource_model):
        attribute_nodes = resource_model.findall('Attributes/Attribute')
        attribute_names = [self.get_attribute_name_from_attribute_node(attribute_node)
                           for attribute_node
                           in attribute_nodes]
        return attribute_names

    def get_class_name_from_model_node(self, model_node):
        resource_model = model_node.attrib['Name']
        return ResourceModelParser.get_resource_model_class_name(resource_model)

    def get_attribute_name_from_attribute_node(self, attribute_node):
        return ResourceModelParser.get_property_name_from_attribute_name(attribute_node.attrib['Name'])


