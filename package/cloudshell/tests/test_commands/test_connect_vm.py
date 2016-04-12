from unittest import TestCase
from mock import Mock, create_autospec
from pyVmomi import vim
from cloudshell.cp.vcenter.commands.connect_dvswitch import VirtualSwitchConnectCommand
from cloudshell.cp.vcenter.vm.dvswitch_connector import VmNetworkMapping
from cloudshell.cp.vcenter.vm.portgroup_configurer import VNicDeviceMapper


class TestVirtualSwitchToMachineDisconnectCommand(TestCase):

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

        vnic_device_mapper = create_autospec(spec=VNicDeviceMapper)
        vnic_device_mapper.vnic = create_autospec(spec=vim.vm.device.VirtualEthernetCard)
        vnic_device_mapper.vnic.macAddress = 'AA-BB'
        vnic_device_mapper.vnic.deviceInfo = Mock()
        vnic_device_mapper.vnic.deviceInfo.label = 'AA-BB'
        vnic_device_mapper.network = Mock()
        vnic_device_mapper.network.name = 'the network'
        vnic_device_mapper.network.key = 'keyyyyyey'
        vnic_device_mapper.requested_vnic = 'requested'

        self.dv_connector = Mock()
        self.dv_connector.connect_by_mapping = Mock(return_value=[vnic_device_mapper])
        self.dv_port_name_gen = Mock()
        self.vlan_spec_factory = Mock()
        self.vlan_id_range_parser = Mock()
        self.vlan_id_range_parser.parse_vlan_id = Mock(return_value=self.vlan_id_gen)
        self.dv_port_name_gen.generate_port_group_name = Mock(return_value=self.name_gen)
        self.vlan_spec_factory.get_vlan_spec = Mock(return_value=self.spec)

    def test_connect_vnic_to_network(self):
        # arrange
        connect_command = VirtualSwitchConnectCommand(self.pv_service, self.dv_connector, self.dv_port_name_gen,
                                                      self.vlan_spec_factory, self.vlan_id_range_parser)
        mapping = VmNetworkMapping()
        mapping.vnic_name = 'name'
        mapping.vlan_id = 'vlan_id'
        mapping.vlan_spec = 'trunc'
        mapping.dv_port_name = 'port_name'
        mapping.network = Mock()

        # act
        connect_results = connect_command.connect_to_networks(si=self.si,
                                                              logger=Mock(),
                                                              vm_uuid=self.vm_uuid,
                                                              vm_network_mappings=[mapping],
                                                              default_network_name='default_network',
                                                              reserved_networks=[],
                                                              dv_switch_name='')

        # assert
        self.assertTrue(self.vlan_id_range_parser.parse_vlan_id.called_with(self.vlan_id))
        self.assertTrue(
            self.dv_port_name_gen.generate_port_group_name.called_with(self.vlan_id, self.vlan_spec_factory))
        self.assertTrue(self.vlan_spec_factory.get_vlan_spec.called_with(self.spec_type))
        self.assertTrue(self.dv_connector.connect_by_mapping.called_with(self.si, self.vm, [mapping]))
        self.assertEqual(connect_results[0].mac_address, 'AA-BB')
