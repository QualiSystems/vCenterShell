from unittest import TestCase

import jsonpickle
from mock import Mock
from pyVim.connect import SmartConnect, Disconnect

from common.vcenter.task_waiter import SynchronousTaskWaiter
from common.vcenter.vmomi_service import pyVmomiService
from tests.utils.testing_credentials import TestCredentials
from vCenterShell.commands.connect_orchestrator import ConnectionCommandOrchestrator
from vCenterShell.network.dvswitch.creator import DvPortGroupCreator
from vCenterShell.network.dvswitch.name_generator import DvPortGroupNameGenerator
from vCenterShell.network.vnic.vnic_service import VNicService
from vCenterShell.vm.dvswitch_connector import VmNetworkMapping, VirtualSwitchToMachineConnector
from vCenterShell.vm.portgroup_configurer import VirtualMachinePortGroupConfigurer
from vCenterShell.vm.vnic_to_network_mapper import VnicToNetworkMapper
from pyVmomi import vim


class TestConnectBulk(TestCase):
    def setUp(self):
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cred = TestCredentials()
        self.si = py_vmomi_service.connect(cred.host, cred.username, cred.password, cred.port)
        synchronous_task_waiter = SynchronousTaskWaiter()
        mapper = VnicToNetworkMapper(DvPortGroupNameGenerator())
        dv_port_group_creator = DvPortGroupCreator(py_vmomi_service, synchronous_task_waiter)
        virtual_machine_port_group_configurer = VirtualMachinePortGroupConfigurer(py_vmomi_service,
                                                                                  synchronous_task_waiter,
                                                                                  mapper,
                                                                                  VNicService())

        connector = VirtualSwitchToMachineConnector(
            dv_port_group_creator,
            virtual_machine_port_group_configurer)

        self.vc_data_model = Mock()
        self.vc_data_model.default_dvswitch_path = 'QualiSB'
        self.vc_data_model.default_dvswitch_name = 'dvSwitch'
        self.vc_data_model.default_port_group_path = 'QualiSB'
        self.vc_data_model.default_network = 'QualiSB/anetwork'
        self.orc_connection = ConnectionCommandOrchestrator(self.vc_data_model, connector)

    def test_connect_bulk(self):
        json = self._get_json()
        results = self.orc_connection.connect_bulk(self.si, json)
        print results

    def _get_json(self):
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
                                "attributeValue": "422239d1-718a-f918-8eca-a70f0667dbbf",
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
                                "attributeValue": "422239d1-718a-f918-8eca-a70f0667dbbf",
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
                                "attributeValue": "422239d1-718a-f918-8eca-a70f0667dbbf",
                                "type": "customAttribute"
                            }
                        ],
                        "type": "setVlan"
                    }
                ]
            }
        })
