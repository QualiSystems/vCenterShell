from unittest import TestCase

from mock import Mock
from pyVmomi import vim
from cloudshell.cp.vcenter.vm.dvswitch_connector import VirtualSwitchToMachineConnector
from cloudshell.cp.vcenter.vm.portgroup_configurer import *
from cloudshell.cp.vcenter.vm.vnic_to_network_mapper import VnicToNetworkMapper

from cloudshell.cp.vcenter.common.cloud_shell.conn_details_retriever import ResourceConnectionDetailsRetriever
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.cp.vcenter.common.utilites.common_name import generate_unique_name


class TestVirtualSwitchToMachineConnector(TestCase):
    def setUp(self):
        self._si = None
        self.virtual_machine_path = 'SergiiT'
        self.virtual_machine_name = 'JustTestNeedToBeRemoved'
        self.vm_uuid = "422254d5-5226-946e-26fb-60c21898b731"

        self.vcenter_name = "QualiSB"
        self.dv_switch_path = 'QualiSB'
        self.network_path = 'QualiSB'

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

        resource_model_parser = ResourceModelParser()
        # vc_model_retriever = VCenterDataModelRetriever(helpers, resource_model_parser, cloudshell_data_retriever_service)
        # vc_data_model = vc_model_retriever.get_vcenter_data_model()
        vc_data_model = Mock()
        name_generator = generate_unique_name
        # vnic_to_network_mapper = VnicToNetworkMapper(name_generator, vc_data_model.default_network)
        vnic_to_network_mapper = VnicToNetworkMapper(name_generator)

        helpers = Mock()
        cs_retriever_service = Mock()
        session = Mock()
        resource_context = Mock()
        connection_details = Mock()

        helpers.get_resource_context_details = Mock(return_value=resource_context)
        helpers.get_api_session = Mock(return_value=session)
        cs_retriever_service.getVCenterConnectionDetails = Mock(return_value=connection_details)

        self.connection_details_retriever = ResourceConnectionDetailsRetriever(helpers)
        self.configurer = VirtualMachinePortGroupConfigurer(self.py_vmomi_service,
                                                            self.synchronous_task_waiter,
                                                            vnic_to_network_mapper,
                                                            Mock(), Mock())

        # pyvmomi_service, synchronous_task_waiter, vnic_to_network_mapper, vnic_common

        self.creator = DvPortGroupCreator(self.py_vmomi_service, self.synchronous_task_waiter)
        self.connector = VirtualSwitchToMachineConnector(self.creator, self.configurer)

    def test_map_vnc(self):
        network_spec = Mock()
        network_spec.dv_port_name = ""
        network_spec.dv_switch_name = ""
        network_spec.dv_switch_path = ""
        network_spec.vlan_id = ""
        network_spec.vlan_spec = ""
        mapp = [network_spec]

        self.configurer.connect_vnic_to_networks = Mock(return_value="OK")
        self.connector.virtual_machine_port_group_configurer.connect_by_mapping = Mock(return_value="OK")
        self.connector.connect_and_get_vm = Mock(return_value=(1, 1,))

        res = self.connector.connect_by_mapping(self.si, self.vm, [], 'default_network', [], logger=Mock())
        self.assertEqual(res, 'OK')
        res = self.connector.connect_by_mapping(self.si, self.vm, [], None, [], logger=Mock())
        self.assertEqual(res, 'OK')

        res = self.connector.connect_by_mapping(self.si, self.vm, mapp, 'default_network', [], logger=Mock())
        self.assertEqual(res, 'OK')
        res = self.connector.connect_by_mapping(self.si, self.vm, mapp, None, [], logger=Mock())
        self.assertEqual(res, 'OK')
