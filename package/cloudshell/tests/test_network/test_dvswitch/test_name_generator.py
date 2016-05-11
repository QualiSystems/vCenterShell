from unittest import TestCase

from cloudshell.cp.vcenter.network.dvswitch.name_generator import DvPortGroupNameGenerator


class TestDvPortGroupCreator(TestCase):
    def test_name(self):
        # arrange
        gen = DvPortGroupNameGenerator()

        # act
        name = gen.generate_port_group_name('some_dv_switch', 'id', 'Trunk')

        # assert
        self.assertEqual('QS_some_dv_switch_VLAN_id_Trunk', name)

    def test_long_dvswitch_name(self):
        # arrange
        gen = DvPortGroupNameGenerator()
        dv_switch_name = "some_dv_switch__some_dv_switch__some_dv_switch__some_dv_switch__some_dv_switch__some_dv_switch__some_dv_switch_"

        # act
        name = gen.generate_port_group_name(dv_switch_name, 'id', 'Trunk')

        # assert
        self.assertEqual('QS_some_dv_switch__some_dv_switch__some_dv_switch__some_dv_swit_VLAN_id_Trunk', name)
