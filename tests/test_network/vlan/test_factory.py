from unittest import TestCase

from cloudshell.cp.vcenter.network.vlan.factory import VlanSpecFactory


class TestVlanSpecFactory(TestCase):

    def test_get_vlan_spec(self):
        vlan_spec_factory = VlanSpecFactory()
        vlan_spec = vlan_spec_factory.get_vlan_spec('Access')
        self.assertIsNotNone(vlan_spec)
