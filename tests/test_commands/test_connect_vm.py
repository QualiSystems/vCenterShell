from unittest import TestCase
from mock import Mock, create_autospec
from common.logger.service import LoggingService
from vCenterShell.commands.connect_dvswitch import VirtualSwitchConnectCommand
from vCenterShell.vm.dvswitch_connector import VmNetworkMapping
from vCenterShell.vm.portgroup_configurer import VNicDeviceMapper
from pyVmomi import vim


class TestVirtualSwitchToMachineDisconnectCommand(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def setUp(self):
        self.vlan_id_gen = 'gen_id'
        self.name_gen = 'gen_name'
        self.spec = Mock()
        self.vm = Mock()
        self.pv_service = Mock()
        self.pv_service.find_by_uuid = Mock(self.vm)
        self.si = Mock()
        self.vm_uuid = 'uuid'
        self.vlan_id = 100
        self.spec_type = Mock()
        self.vcenter_context = Mock()
        self.vcenter_context.default_dvswitch_path = 'default_dvswitch_path'
        self.vcenter_context.default_dvswitch_name = 'default_dvswitch_name'
        self.vcenter_context.default_port_group_path = 'default_port_group_path'

        vnic_device_mapper = create_autospec(spec=VNicDeviceMapper)
        vnic_device_mapper.vnic = create_autospec(spec=vim.vm.device.VirtualEthernetCard)
        vnic_device_mapper.vnic.macAddress = 'AA-BB'

        self.dv_connector = Mock()
        self.dv_connector.connect_by_mapping = Mock(return_value=[vnic_device_mapper])
        self.dv_port_name_gen = Mock()
        self.vlan_spec_factory = Mock()
        self.vlan_id_range_parser = Mock()
        self.vlan_id_range_parser.parse_vlan_id = Mock(return_value=self.vlan_id_gen)
        self.dv_port_name_gen.generate_port_group_name =Mock(return_value=self.name_gen)
        self.vlan_spec_factory.get_vlan_spec = Mock(return_value=self.spec)

    def test_connect_vnic_to_network(self):
        # arrange
        connect_command = VirtualSwitchConnectCommand(self.pv_service, self.dv_connector, self.dv_port_name_gen,
                                                      self.vlan_spec_factory, self.vlan_id_range_parser, Mock())
        mapping = VmNetworkMapping()
        mapping.vnic_name = 'name'
        mapping.vlan_id = 'vlan_id'
        mapping.vlan_spec = 'trunc'
        mapping.dv_port_name = 'port_name'

        # act
        connect_results = connect_command.connect_to_networks(self.si, self.vm_uuid, [mapping], 'default_network')

        mapping.dv_switch_path = self.vcenter_context.default_dvswitch_path
        mapping.dv_switch_name = self.vcenter_context.default_dvswitch_name
        mapping.port_group_path = self.vcenter_context.default_port_group_path

        # assert
        self.assertTrue(self.vlan_id_range_parser.parse_vlan_id.called_with(self.vlan_id))
        self.assertTrue(self.dv_port_name_gen.generate_port_group_name.called_with(self.vlan_id))
        self.assertTrue(self.vlan_spec_factory.get_vlan_spec.called_with(self.spec_type))
        self.assertTrue(self.dv_connector.connect_by_mapping.called_with(self.si, self.vm, [mapping]))
        self.assertEqual(connect_results[0].mac_address, 'AA-BB')
