from unittest import TestCase

from cloudshell.cp.vcenter.network.dvswitch.name_generator import DvPortGroupNameGenerator


class TestDvPortGroupCreator(TestCase):
    def test_name(self):
        # arrange
        gen = DvPortGroupNameGenerator()

        # act
        name = gen.generate_port_group_name('id', 'Trunk')

        # assert
        self.assertEqual('QS_VLAN_id_Trunk', name)
