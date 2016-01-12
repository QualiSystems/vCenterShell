from common.utilites.common_utils import represents_int


class VlanResolverProvider(object):
    def __init__(self, vlan_resource_model, pool_id, reservation_id, owner_id, api):
        """
        :param vlan_resource_model: it can be VLANAutoResourceModel or VLANManualResourceModel
        :param pool_id:
        :param reservation_id:
        :param owner_id:
        :param api: testshell_api session
        :return:
        """
        self.owner_id = owner_id
        self.reservation_id = reservation_id
        self.vlan_resource_model = vlan_resource_model
        self.pool_id = pool_id
        self.api = api

    def resolve_vlan_auto(self):
        """
        Resolves a vlan id automatically based on the data from the VlanResourceModel
        :return: resolved vlan id
        """
        if self.is_vlan_resolved():
            return self.vlan_resource_model.virtual_network

        requested_vlan = self._get_requested_vlan()

        if isinstance(requested_vlan, self.VlanRange):
            vlan_range = requested_vlan
            result = self.api.GetVlanAutoSelectFirstNumericFromRange(
                    self.pool_id,
                    self.reservation_id,
                    self.owner_id,
                    self.vlan_resource_model.isolation_level,
                    vlan_range.start,
                    vlan_range.end)
        else:
            result = self.api.GetVlanSpecificNumeric(
                    self.pool_id,
                    self.reservation_id,
                    self.owner_id,
                    self.vlan_resource_model.isolation_level,
                    requested_vlan)

        return result.VlanId

    def is_vlan_resolved(self):
        if not self.vlan_resource_model.virtual_network.strip():
            return False
        return True

    def _get_requested_vlan(self):
        """
        returns the requested vlan (specific numeric OR numeric range)
        :return: numeric vlan id OR numeric vlan range
        """
        self._ensure_vlan_id_not_empty()

        allocation_range = self._get_allocation_range()

        if self._is_vlan_id_range():
            vlan_range = self._get_vlan_range_from_vlan_id()
            self._ensure_vlan_range_valid(vlan_range, allocation_range)
            return vlan_range
        else:
            self._ensure_numeric_vlan_valid(allocation_range)
            return int(self.vlan_resource_model.vlan_id)

    def _ensure_vlan_id_not_empty(self):
        if not self.vlan_resource_model.vlan_id:
            raise ValueError("VLAN Id attribute is empty")

    def _ensure_vlan_range_valid(self, requested_range, allocation_range):
        if requested_range.start < allocation_range.start or requested_range.end > allocation_range.end:
            raise ValueError("VLAN Id range is outside of the allocated range {0}"
                             .format(self.vlan_resource_model.allocation_ranges))

    def _ensure_numeric_vlan_valid(self, allocation_range):
        if not represents_int(self.vlan_resource_model.vlan_id):
            raise ValueError("VLAN Id attribute value is not numeric")
        numeric_vlan = int(self.vlan_resource_model.vlan_id)
        if numeric_vlan < allocation_range.start or numeric_vlan > allocation_range.end:
            raise ValueError("VLAN Id is outside of the allocated range {0}"
                             .format(self.vlan_resource_model.allocation_ranges))

    def _is_vlan_id_range(self):
        return self.vlan_resource_model.vlan_id.find('-') > 0

    def _get_vlan_range_from_vlan_id(self):
        return self._get_numeric_range_from_range_string(self.vlan_resource_model.vlan_id)

    def _get_allocation_range(self):
        return self._get_numeric_range_from_range_string(self.vlan_resource_model.allocation_ranges)

    def _get_numeric_range_from_range_string(self, range_string):
        start, end = range_string.split("-", 2)
        return self.VlanRange(int(start), int(end))

    class VlanRange(object):
        """
        Inner class that represents a numeric vlan range
        """

        def __init__(self, start, end):
            self.start = start
            self.end = end
