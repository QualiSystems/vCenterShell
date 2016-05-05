import jsonpickle
from mock import Mock
from unittest import TestCase
from cloudshell.cp.vcenter.vm.portgroup_configurer import VNicDeviceMapper
from cloudshell.cp.vcenter.models.ActionResult import ActionResult
from cloudshell.cp.vcenter.models.DeployDataHolder import DeployDataHolder
from cloudshell.cp.vcenter.models.ConnectionResult import ConnectionResult
from cloudshell.cp.vcenter.network.dvswitch.name_generator import DvPortGroupNameGenerator
from cloudshell.cp.vcenter.commands.connect_orchestrator import ConnectionCommandOrchestrator


class TestCommandOrchestrator(TestCase):
    def setUp(self):
        self.portgroup_name = DvPortGroupNameGenerator()
        self.connector = Mock()
        self.disconnector = Mock()
        self.model_parser = Mock()

        self.vc_data_model = Mock()
        self.vc_data_model.reserved_networks = 'restricted_network1,restricted_network2'
        self.vc_data_model.default_dvswitch = 'dvSwitch'
        self.vc_data_model.default_network = 'Anetwork'
        self.vc_data_model.default_datacenter = 'datacenter'
        self.vc_data_model.holding_network = 'Holding Network'

        self.si = Mock()

        self.ConnectionCommandOrchestrator = ConnectionCommandOrchestrator(self.connector,
                                                                           self.disconnector,
                                                                           self.model_parser)

    def test_connect_bulk_dvswitch_is_None(self):
        """
        tests the error by missing dvswitch
        """
        vc_data_model = Mock()
        vc_data_model.reserved_networks = 'restricted_network1,restricted_network2'
        vc_data_model.default_dvswitch = None
        vc_data_model.default_network = 'Anetwork'
        vc_data_model.default_datacenter = 'datacenter'
        vc_data_model.holding_network = 'Holding Network'

        request, expected = self._get_missing_dv_switch_params()
        results = self.ConnectionCommandOrchestrator.connect_bulk(si=self.si,
                                                                  logger=Mock(),
                                                                  vcenter_data_model=vc_data_model,
                                                                  request=request)
        self._assert_as_expected(results, expected)

    def test_connect_bulk1(self):
        """
        Simple connect vm to vlan 'Access' mode
        """
        request, expected = self._get_test1_params()
        results = self.ConnectionCommandOrchestrator.connect_bulk(si=self.si,
                                                                  logger=Mock(),
                                                                  vcenter_data_model=self.vc_data_model,
                                                                  request=request)
        self._assert_as_expected(results, expected)

    def test_connect_bulk2(self):
        """
        Simple disconnect
        """
        request, expected = self._get_test2_params()
        results = self.ConnectionCommandOrchestrator.connect_bulk(si=self.si,
                                                                  logger=Mock(),
                                                                  vcenter_data_model=self.vc_data_model,
                                                                  request=request)
        self._assert_as_expected(results, expected)

    def test_connect_bulk3(self):
        """
        Complex connect multiple vms and multiple vlan types
        """
        request, expected = self._get_test3_params()
        results = self.ConnectionCommandOrchestrator.connect_bulk(si=self.si,
                                                                  logger=Mock(),
                                                                  vcenter_data_model=self.vc_data_model,
                                                                  request=request)
        self._assert_as_expected(results, expected)

    def test_connect_bulk4(self):
        """
        Simple disconnect
        """
        request, expected = self._get_test4_params()
        self.assertRaises(ValueError,
                          self.ConnectionCommandOrchestrator.connect_bulk, self.si, Mock(), self.vc_data_model, request)

    def test_connect_bulk5(self):
        """
        Disconnect returns error
        """
        request, expected = self._get_test5_params()
        res = self.ConnectionCommandOrchestrator.connect_bulk(si=self.si,
                                                              logger=Mock(),
                                                              vcenter_data_model=self.vc_data_model,
                                                              request=request)
        self._assert_as_expected(res, expected)

    def test_connect_bulk6(self):
        """
        Connect returns error
        """
        request, expected = self._get_test6_params()
        res = self.ConnectionCommandOrchestrator.connect_bulk(si=self.si,
                                                              logger=Mock(),
                                                              vcenter_data_model=self.vc_data_model,
                                                              request=request)
        self._assert_as_expected(res, expected)

    def _assert_as_expected(self, res, exp):
        for r in res:
            for e in exp:
                found = e.actionId == r.actionId
                if found:
                    for prop in [prop for prop in dir(r) if not prop.startswith('__')]:
                        self.assertEqual(getattr(r, prop), getattr(e, prop))
                    break

    def _set_connect_to_networks_by_request(self, request):
        a = DeployDataHolder(request['driverRequest'])
        res = []
        for action in a.actions:
            vm_uuid = self.ConnectionCommandOrchestrator._get_vm_uuid(action)
            vnic_name = self.ConnectionCommandOrchestrator._validate_vnic_name(
                self.ConnectionCommandOrchestrator._get_vnic_name(action))
            vlan_id = action.connectionParams.vlanId
            mode = action.connectionParams.mode
            interface = self._get_interface_name(action)
            r = ConnectionResult(mac_address=interface,
                                 vnic_name=vnic_name,
                                 requested_vnic=vnic_name,
                                 vm_uuid=vm_uuid,
                                 network_name=self.portgroup_name.generate_port_group_name('dvSwitch', vlan_id, mode),
                                 network_key='aa')
            res.append(r)
        self.connector.connect_to_networks = Mock(return_value=res)

    def _set_disconnect_from_networks(self, request):
        a = DeployDataHolder(request['driverRequest'])
        res = []
        for action in a.actions:
            vnic_name = self.ConnectionCommandOrchestrator._validate_vnic_name(
                self.ConnectionCommandOrchestrator._get_vnic_name(action))
            interface = self._get_interface_name(action)
            r = VNicDeviceMapper(vnic=Mock(), requested_vnic=vnic_name, network=Mock(), connect=False, mac=interface)
            res.append(r)
        self.disconnector.disconnect_from_networks = Mock(return_value=res)

    def _get_interface_name(self, action):
        interface_attributes = [attr.attributeValue
                                for attr in action.connectorAttributes
                                if attr.attributeName == 'Interface']
        interface = 'aa' if not interface_attributes else interface_attributes[0]
        return interface

    def _get_connect_excepted_results(self, request, error_msg=None, ignore_interface=False):
        a = DeployDataHolder(request['driverRequest'])
        res = []
        for action in a.actions:
            r = ActionResult()
            r.actionId = action.actionId
            r.type = action.type
            r.errorMessage = error_msg
            r.infoMessage = 'VLAN successfully set' if not error_msg else None
            r.success = True if not error_msg else False
            r.updatedInterface = None if ignore_interface else self._get_interface_name(action)
            res.append(r)
        return res

    def _get_disconnect_excepted_results(self, request, error_msg=None):
        a = DeployDataHolder(request['driverRequest'])
        res = []
        for action in a.actions:
            r = ActionResult()
            r.actionId = action.actionId
            r.type = action.type
            r.errorMessage = error_msg
            r.infoMessage = 'VLAN Successfully removed' if not error_msg else None
            r.success = True if not error_msg else False
            r.updatedInterface = self._get_interface_name(action)
            res.append(r)
        return res

    def _get_missing_dv_switch_params(self):
        request = {
            'driverRequest': {
                'actions': [
                    {
                        "connectorAttributes": [],
                        "connectionParams": {
                            "vlanId": "2",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Access",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "actionId": "ee8a3dc8-eb4b-4141-92ad-58bbd8430cad_376046bb-1ef0-4ecc-bb52-c0c7a9c75b1c",
                        "actionTarget": {
                            "fullName": "VM Deployment1_9602ad34",
                            "fullAddress": "N/A/NA",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220ae6-2fa8-b4cd-14e4-16fbad2798f6",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    }
                ]
            }
        }
        self._set_connect_to_networks_by_request(request)
        expected = self._get_connect_excepted_results(request,
                                                      error_msg='Please set the attribute "Default DvSwitch" in order to execute any connectivity changes',
                                                      ignore_interface=True)
        return jsonpickle.encode(request), expected

    def _get_test1_params(self):
        request = {
            'driverRequest': {
                'actions': [
                    {
                        "connectorAttributes": [],
                        "connectionParams": {
                            "vlanId": "2",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Access",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "actionId": "ee8a3dc8-eb4b-4141-92ad-58bbd8430cad_376046bb-1ef0-4ecc-bb52-c0c7a9c75b1c",
                        "actionTarget": {
                            "fullName": "VM Deployment1_9602ad34",
                            "fullAddress": "N/A/NA",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220ae6-2fa8-b4cd-14e4-16fbad2798f6",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    }
                ]
            }
        }
        self._set_connect_to_networks_by_request(request)
        expected = self._get_connect_excepted_results(request)
        return jsonpickle.encode(request), expected

    def _get_test2_params(self):
        request = {
            "driverRequest": {
                "actions": [
                    {
                        "connectionId": "d5369772-66de-4003-85cc-e94a57c20f1e",
                        "connectionParams": {
                            "vlanId": "654",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Access",
                                    "type": "vlanServiceAttribute"
                                },
                                {
                                    "attributeName": "VLAN ID",
                                    "attributeValue": "654",
                                    "type": "vlanServiceAttribute"
                                },
                                {
                                    "attributeName": "Virtual Network",
                                    "attributeValue": "654",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "connectorAttributes": [
                            {
                                "attributeName": "Interface",
                                "attributeValue": "00:50:56:a2:5f:07",
                                "type": "connectorAttribute"
                            }
                        ],
                        "actionId": "d5369772-66de-4003-85cc-e94a57c20f1e_30fb5d10-1ce9-4e9f-b41e-ce0d271fd7ab",
                        "actionTarget": {
                            "fullName": "Temp4_a443da02",
                            "fullAddress": "192.168.65.33",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "422279bf-5899-789f-ca44-2c62075b3d2d",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "removeVlan"
                    }
                ]
            }
        }
        self._set_disconnect_from_networks(request)
        expected = self._get_disconnect_excepted_results(request)
        return jsonpickle.encode(request), expected

    def _get_test3_params(self):
        request = {
            'driverRequest': {
                'actions': [
                    {
                        "connectorAttributes": [],
                        "connectionParams": {
                            "vlanId": "2",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Access",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "actionId": "1",
                        "actionTarget": {
                            "fullName": "VM Deployment1_9602ad34",
                            "fullAddress": "N/A/NA",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220ae6-2fa8-b4cd-14e4-16fbad2798f6",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    },
                    {
                        "connectorAttributes": [],
                        "connectionParams": {
                            "vlanId": "2-10",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Trunk",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "actionId": "2",
                        "actionTarget": {
                            "fullName": "VM Deployment1_9602ad34",
                            "fullAddress": "N/A/NA",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220ae6-2fa8-b4cd-14e4-16fbad2798f6",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    },
                    {
                        "connectorAttributes": [],
                        "connectionParams": {
                            "vlanId": "2",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Access",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "actionId": "3",
                        "actionTarget": {
                            "fullName": "VM Deployment1_9602ad34",
                            "fullAddress": "N/A/NA",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220ae6-2fa8-b4cd-14e4-16fbad2798f6",
                                "type": "customAttribute"
                            },
                            {
                                "attributeName": "Vnic Name",
                                "attributeValue": "1",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    },
                    {
                        "connectorAttributes": [],
                        "connectionParams": {
                            "vlanId": "2",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Access",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "actionId": "4",
                        "actionTarget": {
                            "fullName": "VM Deployment1_9602ad34",
                            "fullAddress": "N/A/NA",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "1234",
                                "type": "customAttribute"
                            },
                            {
                                "attributeName": "Vnic Name",
                                "attributeValue": "1",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    }
                ]
            }
        }
        self._set_connect_to_networks_by_request(request)
        expected = self._get_connect_excepted_results(request)
        return jsonpickle.encode(request), expected

    def _get_test4_params(self):
        request = {
            "driverRequest": {
                "actions": [
                    {
                        "connectionId": "d5369772-66de-4003-85cc-e94a57c20f1e",
                        "connectionParams": {
                            "vlanId": "654",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Access",
                                    "type": "vlanServiceAttribute"
                                },
                                {
                                    "attributeName": "VLAN ID",
                                    "attributeValue": "654",
                                    "type": "vlanServiceAttribute"
                                },
                                {
                                    "attributeName": "Virtual Network",
                                    "attributeValue": "654",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "connectorAttributes": [
                            {
                                "attributeName": "Interface",
                                "attributeValue": "00:50:56:a2:5f:07",
                                "type": "connectorAttribute"
                            }
                        ],
                        "actionId": "d5369772-66de-4003-85cc-e94a57c20f1e_30fb5d10-1ce9-4e9f-b41e-ce0d271fd7ab",
                        "actionTarget": {
                            "fullName": "Temp4_a443da02",
                            "fullAddress": "192.168.65.33",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                        ],
                        "type": "removeVlan"
                    }
                ]
            }
        }
        self._set_disconnect_from_networks(request)
        expected = self._get_disconnect_excepted_results(request, 'VM_UUID is missing on action attributes')
        return jsonpickle.encode(request), expected

    def _get_test5_params(self):
        request = {
            "driverRequest": {
                "actions": [
                    {
                        "connectionId": "d5369772-66de-4003-85cc-e94a57c20f1e",
                        "connectionParams": {
                            "vlanId": "654",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Access",
                                    "type": "vlanServiceAttribute"
                                },
                                {
                                    "attributeName": "VLAN ID",
                                    "attributeValue": "654",
                                    "type": "vlanServiceAttribute"
                                },
                                {
                                    "attributeName": "Virtual Network",
                                    "attributeValue": "654",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "connectorAttributes": [
                            {
                                "attributeName": "Interface",
                                "attributeValue": "00:50:56:a2:5f:07",
                                "type": "connectorAttribute"
                            }
                        ],
                        "actionId": "d5369772-66de-4003-85cc-e94a57c20f1e_30fb5d10-1ce9-4e9f-b41e-ce0d271fd7ab",
                        "actionTarget": {
                            "fullName": "Temp4_a443da02",
                            "fullAddress": "192.168.65.33",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220ae6-2fa8-b4cd-14e4-16fbad2798f6",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "removeVlan"
                    }
                ]
            }
        }
        self.disconnector.disconnect_from_networks = Mock()
        self.disconnector.disconnect_from_networks.side_effect = ValueError('vnic not found')
        expected = self._get_disconnect_excepted_results(request, 'vnic not found')
        return jsonpickle.encode(request), expected

    def _get_test6_params(self):
        request = {
            'driverRequest': {
                'actions': [
                    {
                        "connectorAttributes": [],
                        "connectionParams": {
                            "vlanId": "2",
                            "mode": "Access",
                            "vlanServiceAttributes": [
                                {
                                    "attributeName": "Access Mode",
                                    "attributeValue": "Access",
                                    "type": "vlanServiceAttribute"
                                }
                            ],
                            "type": "setVlanParameter"
                        },
                        "actionId": "ee8a3dc8-eb4b-4141-92ad-58bbd8430cad_376046bb-1ef0-4ecc-bb52-c0c7a9c75b1c",
                        "actionTarget": {
                            "fullName": "VM Deployment1_9602ad34",
                            "fullAddress": "N/A/NA",
                            "type": "actionTarget"
                        },
                        "customActionAttributes": [
                            {
                                "attributeName": "VM_UUID",
                                "attributeValue": "42220ae6-2fa8-b4cd-14e4-16fbad2798f6",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    }
                ]
            }
        }
        self.connector.connect_to_networks = Mock()
        self.connector.connect_to_networks.side_effect = ValueError('vnic not found')
        expected = self._get_connect_excepted_results(request, 'vnic not found')
        # here we don't don't get vnic input input
        for e in expected:
            e.updatedInterface = None
        return jsonpickle.encode(request), expected

