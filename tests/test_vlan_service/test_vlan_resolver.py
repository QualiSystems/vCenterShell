from unittest import TestCase
from mock import Mock, MagicMock
from models.VLANAutoResourceModel import VLANAutoResourceModel
from vlan_service.resolver.provider import VlanResolverProvider


class TestVlanResolver(TestCase):
    def test_vlan_service_not_resolved_yet(self):
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

    def test_vlan_service_already_resolved(self):
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

    def test_vlan_service_get_allocation_range(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "20"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-30"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        allocation_range = resolver._get_allocation_range()

        self.assertEquals(allocation_range.start, 10)
        self.assertEquals(allocation_range.end, 30)

    def test_vlan_service_get_vlan_range_from_vlan_id(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "200-400"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-30"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        requested_range = resolver._get_vlan_range_from_vlan_id()

        self.assertEquals(requested_range.start, 200)
        self.assertEquals(requested_range.end, 400)

    def test_vlan_service_is_vlan_id_range_true(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "200-400"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-30"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        self.assertTrue(resolver._is_vlan_id_range())

    def test_vlan_service_is_vlan_id_range_false(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "20"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-30"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        self.assertFalse(resolver._is_vlan_id_range())

    def test_vlan_service_requested_range_outside_of_allocated_range(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "2-100"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-30"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        requested_vlan_range = resolver._get_vlan_range_from_vlan_id()
        allocation_range = resolver._get_allocation_range()

        self.assertRaises(ValueError, resolver._ensure_vlan_range_valid, requested_vlan_range, allocation_range)

    def test_vlan_service_requested_vlan_not_numeric(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "stam"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-30"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        allocation_range = resolver._get_allocation_range()

        self.assertRaises(ValueError, resolver._ensure_numeric_vlan_valid, allocation_range)

    def test_vlan_service_requested_specific_vlan_numeric_outside_of_allocated_range(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "50"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-30"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        allocation_range = resolver._get_allocation_range()

        self.assertRaises(ValueError, resolver._ensure_numeric_vlan_valid, allocation_range)

    def test_vlan_service_get_requested_vlan_returns_range(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "20-30"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-30"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        requested_range = resolver._get_requested_vlan()

        self.assertEquals(requested_range.start, 20)
        self.assertEquals(requested_range.end, 30)

    def test_vlan_service_get_requested_vlan_returns_numeric(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "20"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-30"

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=Mock())

        vlan = resolver._get_requested_vlan()

        self.assertEquals(vlan, 20)

    def test_vlan_service_resolves_specific_numeric(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "20"
        vlan_resource_model.isolation_level = "Exclusive"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-100"

        resolved_vlan_info = Mock()
        resolved_vlan_info.VlanId = 20

        api = MagicMock()
        api.GetVlanSpecificNumeric = Mock(return_value=resolved_vlan_info)

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=api)

        resolved_vlan = resolver.resolve_vlan_auto()

        api.GetVlanSpecificNumeric.assert_called_with("Global", "c5144273-c456-4885-a9b7-f5b058f02678",
                                                      "VLAN Auto", "Exclusive", 20)
        self.assertEquals(resolved_vlan, 20)

    def test_vlan_service_resolves_first_numeric_from_range(self):
        vlan_resource_model = VLANAutoResourceModel()
        vlan_resource_model.vlan_id = "20-30"
        vlan_resource_model.isolation_level = "Exclusive"
        vlan_resource_model.virtual_network = ""
        vlan_resource_model.allocation_ranges = "10-100"

        resolved_vlan_info = Mock()
        resolved_vlan_info.VlanId = 20

        api = MagicMock()
        api.GetVlanAutoSelectFirstNumericFromRange = Mock(return_value=resolved_vlan_info)

        resolver = VlanResolverProvider(vlan_resource_model=vlan_resource_model,
                                        pool_id="Global",
                                        reservation_id="c5144273-c456-4885-a9b7-f5b058f02678",
                                        owner_id="VLAN Auto",
                                        api=api)

        resolved_vlan = resolver.resolve_vlan_auto()

        api.GetVlanAutoSelectFirstNumericFromRange.assert_called_with("Global", "c5144273-c456-4885-a9b7-f5b058f02678",
                                                                      "VLAN Auto", "Exclusive", 20, 30)
        self.assertEquals(resolved_vlan, 20)
