from unittest import TestCase

import jsonpickle
from mock import Mock, patch

from tests.utils.testing_credentials import TestCredentials
from vCenterShell.commands.command_orchestrator import CommandOrchestrator


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
        self.command_orchestrator.vc_data_model.default_dvswitch_path = 'QualiSB'
        self.command_orchestrator.vc_data_model.default_dvswitch_name = 'dvSwitch'
        self.command_orchestrator.vc_data_model.default_port_group_path = 'QualiSB'
        self.command_orchestrator.vc_data_model.default_network = 'QualiSB/anetwork'
        self.ports = Mock()
        self.command_orchestrator._parse_remote_model = Mock(return_value=remote_resource)

    def test_connect_bulk(self):
        json = self._get_connect_json()
        results = self.command_orchestrator.connect_bulk(self.context, json)
        print results

    def test_disconnect_bulk(self):
        json = self._get_disconnect_json()
        results = self.command_orchestrator.connect_bulk(self.context, json)
        print results

    def _get_disconnect_json(self):
        return jsonpickle.encode({"driverRequest":{"actions":[{"connectionId":"89a08d5f-bf26-4b9b-b704-843e19bdcd35","connectionParams":{"vlanIds":["2"],"mode":"Access","type":"setVlanParameter"},"connectorAttributes":[{"attributeName":"Interface","attributeValue":"00:50:56:a2:3f:96","type":"connectorAttribute"}],"actionId":"eff31a93-4056-43b7-8d52-dba34aec9d93","actionTarget":{"fullName":"VM Deployment_bd4295cd","fullAddress":"N/A","type":"actionTarget"},"customActionAttributes":[{"attributeName":"VM_UUID","attributeValue":"4222f73c-432f-cb28-caa5-61ba4776950b","type":"customAttribute"}],"type":"removeVlan"}]}})

    def _get_connect_json(self):
        return jsonpickle.encode({
            "driverRequest": {
                "actions": [
                    {
                        "connectionId": "4690f6a3-d18b-4f0d-9937-ae84b50c35c0",
                        "connectionParams": {
                            "vlanIds": [
                                "2"
                            ],
                            "mode": "Access",
                            "type": "setVlanParameter"
                        },
                        "connectorAttributes": [],
                        "actionId": "42d630fa-d52e-4cfd-a329-e43bd6b6b0ae",
                        "actionTarget": {
                            "fullName": "VM Deployment_2fadfcad",
                            "fullAddress": "N/A",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "4222f73c-432f-cb28-caa5-61ba4776950b",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    }
                ]
            }
        })
