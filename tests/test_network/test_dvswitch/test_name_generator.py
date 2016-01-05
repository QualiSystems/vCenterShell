from unittest import TestCase
from vCenterShell.network.dvswitch.name_generator import DvPortGroupNameGenerator


class TestDvPortGroupCreator(TestCase):
    def test_name(self):
        # arrange
        gen = DvPortGroupNameGenerator()

        # act
        name = gen.generate_port_group_name('id')

        # assert
        self.assertEqual('VLAN id', name)
