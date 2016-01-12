from unittest import TestCase
from mock import Mock

from models.VLANAutoResourceModel import VLANAutoResourceModel
from vlan_service.resolver.provider import VlanResolverProvider


class TestVlanResolver(TestCase):
    def test_vlan_resolved_not_resolved_yet(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "20"
        vlan_resource_model.virtual_network = ""

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        result = resolver.is_vlan_resolved()

        self.assertFalse(result)

    def test_vlan_resolved_already_resolved(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "20"
        vlan_resource_model.virtual_network = "20"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        result = resolver.is_vlan_resolved()

        self.assertTrue(result)



