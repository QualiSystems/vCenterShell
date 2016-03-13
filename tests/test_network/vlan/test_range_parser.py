from unittest import TestCase

from cloudshell.cp.vcenter.network.vlan.range_parser import VLanIdRangeParser


class TestVLanIdRangeParser(TestCase):
    def test_one_number(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        vlan_id = v_lan_id_range_parser.parse_vlan_id('Trunk', '11')

        self.assertEqual(vlan_id[0].start, 11)
        self.assertEqual(vlan_id[0].end, 11)

    def test_two_numbers_with_dash(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        vlan_id = v_lan_id_range_parser.parse_vlan_id('Trunk', '11-100')

        self.assertEqual(vlan_id[0].start, 11)
        self.assertEqual(vlan_id[0].end, 100)

    def test_one_number_access_mode(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        vlan_id = v_lan_id_range_parser.parse_vlan_id('Access', '100')

        self.assertEqual(vlan_id, 100)

    def test_parse_vlan_id(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        self.assertRaises(Exception, v_lan_id_range_parser.parse_vlan_id, '', None)

    def test_not_a_number_vlan_id(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        self.assertRaises(KeyError, v_lan_id_range_parser.parse_vlan_id, 'Access', 'a')

    def test_three_vlan_id_parts(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        self.assertRaises(Exception, v_lan_id_range_parser.parse_vlan_id, 'Trunk', '1-100-1000')

    def test_unknown_mode(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        self.assertRaises(KeyError, v_lan_id_range_parser.parse_vlan_id, 'Unknown', '100')