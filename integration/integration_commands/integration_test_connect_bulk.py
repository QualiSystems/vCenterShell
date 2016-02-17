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
                        "connectionId": "1cffa2d4-5507-4db3-9119-8212ebb45b94",
                        "connectionParams": {
                            "vlanIds": [
                                "8"
                            ],
                            "mode": "Access",
                            "type": "setVlanParameter"
                        },
                        "connectorAttributes": [],
                        "actionId": "dbb453a6-d897-482f-b7c4-b3d89447a740",
                        "actionTarget": {
                            "fullName": "VM Deployment_ab14e2b3",
                            "fullAddress": "N/A",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42221c16-d835-b0ab-729d-2b5c702874b4",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "removeVlan"
                    }
                ]
            }
        }
        )

    def _get_connect_json(self):
        return jsonpickle.encode({
            "driverRequest": {
                "actions": [
                    {
                        "connectionId": "c2c7384c-0afc-438e-9a53-95840d98a64f",
                        "connectionParams": {
                            "vlanIds": [
                                "10"
                            ],
                            "mode": "Access",
                            "type": "setVlanParameter"
                        },
                        "connectorAttributes": [

                        ],
                        "actionId": "2bb7f875-25d2-42de-ae8c-6c8acead053b",
                        "actionTarget": {
                            "fullName": "VM Deployment_a2917e64",
                            "fullAddress": "N/A",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220987-0ec2-b9f0-0c47-1034fd25bac7",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    },
                    {
                        "connectionId": "0bf012ab-06ec-41a9-8e48-bbc4609f4d31",
                        "connectionParams": {
                            "vlanIds": [
                                "9"
                            ],
                            "mode": "Access",
                            "type": "setVlanParameter"
                        },
                        "connectorAttributes": [

                        ],
                        "actionId": "bb40973d-8ef5-4235-ac26-7332153f5e50",
                        "actionTarget": {
                            "fullName": "VM Deployment_a2917e64",
                            "fullAddress": "N/A",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220987-0ec2-b9f0-0c47-1034fd25bac7",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    },
                    {
                        "connectionId": "fb8a2512-4d04-48c7-a6a8-bc52cc6ba717",
                        "connectionParams": {
                            "vlanIds": [
                                "8"
                            ],
                            "mode": "Access",
                            "type": "setVlanParameter"
                        },
                        "connectorAttributes": [

                        ],
                        "actionId": "df3d5406-11f5-4e64-89c5-f681ee099ed9",
                        "actionTarget": {
                            "fullName": "VM Deployment_a2917e64",
                            "fullAddress": "N/A",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220987-0ec2-b9f0-0c47-1034fd25bac7",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    }
                ]
            }
        })
