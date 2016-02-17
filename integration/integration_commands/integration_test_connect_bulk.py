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
        return jsonpickle.encode({
            "driverRequest": {
                "actions": [
                    {
                        "connectionId": "9376d21d-f3a5-4308-83a7-1bf63c281436",
                        "connectionParams": {
                            "vlanIds": [
                                "6"
                            ],
                            "mode": "Access",
                            "type": "setVlanParameter"
                        },
                        "connectorAttributes": [
                            {
                                "attributeName": "Interface",
                                "attributeValue": "00:50:56:a2:7e:15",
                                "type": "connectorAttribute"
                            }
                        ],
                        "actionId": "6d7550d4-19a1-4fac-89ee-fbf4409bbcd9",
                        "actionTarget": {
                            "fullName": "VM Deployment_94b23f88",
                            "fullAddress": "N/A",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "4222fa1a-c0f8-b61d-2dfb-a894274eac7c",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "removeVlan"
                    }
                ]
            }
        })

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
                                "attributeValue": "42229eed-1071-b447-faf5-280412d97501",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    }
                ]
            }
        })
