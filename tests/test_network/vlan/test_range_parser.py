from unittest import TestCase

from vCenterShell.network.vlan.range_parser import VLanIdRangeParser


class TestVLanIdRangeParser(TestCase):
    def test_one_numer(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        vlan_id = v_lan_id_range_parser.parse_vlan_id('11')

        self.assertEqual(vlan_id, 11)

    def test_two_numbers_with_dash(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        vlan_id = v_lan_id_range_parser.parse_vlan_id('11-100')

        self.assertEqual(vlan_id[0].start, 11)
        self.assertEqual(vlan_id[0].end, 100)

    def test_parse_vlan_id(self):
        v_lan_id_range_parser = VLanIdRangeParser()
        self.assertRaises(Exception, v_lan_id_range_parser.parse_vlan_id, None)
