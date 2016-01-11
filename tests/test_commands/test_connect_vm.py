from unittest import TestCase

from mock import Mock, patch
from mock import create_autospec
from pyVmomi import vim

import qualipy.scripts.cloudshell_scripts_helpers as helpers

from common.logger.service import LoggingService
from qualipy.api.cloudshell_api import ResourceInfo

from common.model_factory import ResourceModelParser
from vCenterShell.commands.connect_dvswitch import VirtualSwitchConnectCommand
from vCenterShell.network.dvswitch.creator import DvPortGroupCreator
from common.cloudshell.conn_details_retriever import ResourceConnectionDetailsRetriever
from common.cloudshell.data_retriever import CloudshellDataRetrieverService
from vCenterShell.vm.dvswitch_connector import VirtualSwitchToMachineConnector
from vCenterShell.network.vnic.vnic_common import *
from vCenterShell.vm.portgroup_configurer import *


class TestVirtualSwitchToMachineDisconnectCommand(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def setUp(self):

        self._si = None
        self.virtual_machine_path = 'SergiiT'
        self.virtual_machine_name = 'JustTestNeedToBeRemoved'
        self.vm_uuid = "422254d5-5226-946e-26fb-60c21898b731"

        self.vcenter_name    = "QualiSB"
        self.port_group_path = 'QualiSB'
        self.dv_switch_path  = 'QualiSB'
        self.network_path    = 'QualiSB'

        self.dv_switch_name = 'dvSwitch-SergiiT'
        self.dv_port_group_name = 'aa-dvPortGroup3B'

        self.network = Mock()
        self.network.key = "network-key"
        self.network.config.distributedVirtualSwitch.uuid = "422254d5-5226-946e-26fb-60c21898b73f"
        self.py_vmomi_service = Mock()

        self.vm = Mock()
        self.vm.config.hardware = Mock()
        self.vnic = Mock(spec=vim.vm.device.VirtualEthernetCard)
        self.vnic.deviceInfo = Mock()
        self.vm.config.hardware.device = [self.vnic]

        self.py_vmomi_service.find_by_uuid = lambda a, b, c: self.vm
        self.py_vmomi_service.find_network_by_name = Mock(return_value=self.network)


        self.synchronous_task_waiter = Mock()
        self.synchronous_task_waiter.wait_for_task = Mock(return_value="TASK OK")
        self.si = Mock()


        self.data_retriever_service = CloudshellDataRetrieverService()
        self.connection_details_retriever = ResourceConnectionDetailsRetriever(self.data_retriever_service)
        self.configurer = VirtualMachinePortGroupConfigurer(self.py_vmomi_service, self.synchronous_task_waiter)
        self.creator = DvPortGroupCreator(self.py_vmomi_service, self.synchronous_task_waiter)
        self.connector = VirtualSwitchToMachineConnector(self.py_vmomi_service,
                                                          self.connection_details_retriever,
                                                          self.creator,
                                                          self.configurer)


        inventory_path_data = Mock()
        inventory_path_data.vm_folder = ""
        inventory_path_data.vCenter_resource_name = ""

        self.data_retriever_service.getVCenterInventoryPathAttributeData = Mock(return_value=inventory_path_data)
        vlan_id_range_parser = Mock()
        vlan_id_range_parser.parse_vlan_id = Mock(return_value="")

        dv_port_group_name_generator = Mock()
        dv_port_group_name_generator.generate_port_group_name = Mock(return_value="PG_NAME")

        vlan_spec_factory = Mock()
        vlan_spec_factory.get_vlan_spec = Mock(return_value="")
        self.command = VirtualSwitchConnectCommand(self.data_retriever_service,
                                                   self.connector,
                                                   dv_port_group_name_generator,
                                                   vlan_spec_factory(),
                                                   vlan_id_range_parser,
                                                   ResourceModelParser())

        self.command.inventory_path_data = Mock()
        self.command.inventory_path_data.vCenter_resource_name = "/"
        self.resource_context = self._get_resource_info()

    def _get_resource_info(self):
        resource_info = create_autospec(ResourceInfo)
        resource_info.ResourceModelName = 'VLAN'
        resource_info.attrib = {'Access Mode': 'Trunk', 'VLAN ID': '123', "uuid": "fffffffff"}
        return resource_info

    def test_connect(self):

        @patch("qualipy.scripts.cloudshell_scripts_helpers")
        def get_api_session(*args):
            return Mock()

        resource = Mock()
        resource.ResourceModelName = 'VM'

        self.command.create_context = Mock()
        self.command.session = Mock()
        self.command.session.GetResourceDetails = Mock(return_value=resource)

        model = Mock()
        model.default_dvswitch_path = "/"
        model.default_dvswitch_name = "DWS"
        model.default_port_group_path = "PGN"
        self.command.resourse_model_parser = Mock()
        self.command.resourse_model_parser.convert_to_resource_model = Mock(return_value=model)


        self.connector.connect_specific_vnic = Mock(return_value="OK 1")
        self.connector.connect               = Mock(return_value="OK 2")
        self.connector.connect_networks      = Mock(return_value="OK 3")

        res = self.command.connect_specific_vnic(111, "", "vnic_name")
        self.assertEquals(res, "OK 1")

        res = self.command.connect_to_first_vnic(111, "")
        self.assertEquals(res, "OK 2")

        # res = self.command.connect_vm_to_vlan(111, "")
        # self.assertEquals(res, "OK 2")

        res = self.command.connect_networks(111, "")
        self.assertEquals(res, "OK 3")


