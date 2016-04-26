from unittest import TestCase

import jsonpickle
from mock import Mock, patch

from cloudshell.cp.vcenter.commands.command_orchestrator import CommandOrchestrator
from cloudshell.tests.utils.testing_credentials import TestCredentials


class MockResourceParser(object):
    @staticmethod
    def convert_to_resource_model(dummy, resource):
        return resource


class TestConnectBulk(TestCase):
    @patch('common.model_factory.ResourceModelParser.convert_to_resource_model',
           MockResourceParser.convert_to_resource_model)
    def setUp(self):
        self.resource = Mock()
        self.context = Mock()
        session = Mock()
        remote_resource = Mock()
        remote_resource.fullname = 'this is full name of the remote resource'
        remote_resource.uuid = 'this is full uuis of the remote resource'
        self.connection_details = TestCredentials()
        self.context.resource = self.resource
        self.context.remote_endpoints = [self.resource]
        self.command_orchestrator = CommandOrchestrator(self.context)
        self.command_orchestrator.cs_helper = Mock()
        self.command_orchestrator.cs_helper.get_session = Mock(return_value=session)
        self.command_orchestrator.cs_helper.get_connection_details = Mock(return_value=self.connection_details)
        self.command_orchestrator.vc_data_model.default_dvswitch = 'QualiSB\\dvSwitch'
        self.command_orchestrator.vc_data_model.holding_network = 'QualiSB/anetwork'
        self.ports = Mock()
        self.command_orchestrator._parse_remote_model = Mock(return_value=remote_resource)
        self.command_orchestrator.connection_orchestrator.disconnector.default_network = \
            self.command_orchestrator.vc_data_model.holding_network

    def test_connect_bulk(self):
        json = self._get_connect_json()
        results = self.command_orchestrator.connect_bulk(self.context, json)
        print results

    def test_disconnect_bulk(self):
        json = self._get_disconnect_json()
        results = self.command_orchestrator.connect_bulk(self.context, json)
        print results

    def _get_disconnect_json(self):
        return jsonpickle.encode({"driverRequest":{"actions":[{"connectionId":"2e85db89-f1c9-4da2-b738-6ed57d7c8ec6","connectionParams":{"vlanIds":["2"],"mode":"Access","type":"setVlanParameter"},"connectorAttributes":[{"attributeName":"Interface","attributeValue":"00:50:56:a2:3c:83","type":"connectorAttribute"}],"actionId":"27409903-4d80-4607-8be2-8140285f87e6","actionTarget":{"fullName":"VM Deployment_6693d80d","fullAddress":"N/A","type":"actionTarget"},"customActionAttributes":[{"attributeName":"VM_UUID","attributeValue":"422279ec-e35a-b63f-591a-5e748514056d","type":"customAttribute"}],"type":"removeVlan"},{"connectionId":"2e85db89-f1c9-4da2-b738-6ed57d7c8ec6","connectionParams":{"vlanIds":["2"],"mode":"Access","type":"setVlanParameter"},"connectorAttributes":[{"attributeName":"Interface","attributeValue":"00:50:56:a2:4f:e2","type":"connectorAttribute"}],"actionId":"20d37283-3f90-4d5b-a949-5851629f20e6","actionTarget":{"fullName":"VM Deployment_44256851","fullAddress":"N/A","type":"actionTarget"},"customActionAttributes":[{"attributeName":"VM_UUID","attributeValue":"422217cb-1de3-1faf-bc42-401e9ecee942","type":"customAttribute"}],"type":"removeVlan"}]}})

    def _get_connect_json(self):
        return jsonpickle.encode({"driverRequest":{"actions":[{"connectionId":"4e7c7249-be28-4bd4-b528-0cb14a18b64d","connectionParams":{"vlanIds":["2"],"mode":"Access","type":"setVlanParameter"},"connectorAttributes":[],"actionId":"f1fcd6c0-f9c2-45f6-8ad2-c996a96e87e7","actionTarget":{"fullName":"VM Deployment_7c6cf268","fullAddress":"N/A","type":"actionTarget"},"customActionAttributes":[{"attributeName":"VM_UUID","attributeValue":"4222a08b-4034-d611-dda4-a45d51828865","type":"customAttribute"}],"type":"setVlan"}]}})
