from common.utilites.common_utils import represents_int
import qualipy.scripts.cloudshell_scripts_helpers as helpers


class VlanServiceProvider(object):

    def __init__(self, vlan_resource_model, pool_id, reservation_id, owner_id, api):
        """
        :param vlan_resource_model: it can be VLANAutoResourceModel or VLANManualResourceModel
        :param pool_id:
        :param reservation_id:
        :param owner_id:
        :param api: cloudshell_api session
        :return:
        """
        self.owner_id = owner_id
        self.reservation_id = reservation_id
        self.vlan_resource_model = vlan_resource_model
        self.pool_id = pool_id
        self.api = api

    def resolve_vlan_auto(self):
        """
        Resolves a vlan id automaticaly based on the data from the VlanResourceModel
        :return: resolved vlan id
        """
        if self.is_vlan_resolved():
            return self.vlan_resource_model.virtual_network

        self.ensure_vlan_id_value_is_ok()

        api = helpers.get_api_session()

        if self.is_vlan_id_range():
            vlan_range = self.get_vlan_range_from_vlan_id()
            result = api.GetVlanAutoSelectFirstNumericFromRange(
                self.pool_id,
                self.reservation_id,
                self.owner_id,
                self.vlan_resource_model.isolation_level,
                vlan_range.start,
                vlan_range.end)
        else:
            result = api.GetVlanSpecificNumeric(
                self.pool_id,
                self.reservation_id,
                self.owner_id,
                self.vlan_resource_model.isolation_level,
                self.vlan_resource_model.vlan_id)

        #todo if result is success set VirtualNetwork attribute

    def ensure_vlan_id_value_is_ok(self):
        """ validate that the vlan id value is ok """
        if not self.vlan_resource_model.vlan_id:
            raise ValueError("VLAN Id attribute is empty")

        allocation_range = self.get_allocation_range()

        if self.is_vlan_id_range():
            vlan_range = self.get_vlan_range_from_vlan_id()
            if vlan_range.start < allocation_range.start or vlan_range.end > allocation_range.end:
                raise ValueError("VLAN Id range is outside of the allocated range {0}".format(
                    self.vlan_resource_model.allocation_range))
        else:
            if not represents_int(self.vlan_resource_model.vlan_id):
                raise ValueError("VLAN Id attribute value is not numeric")
            numeric_vlan = int(self.vlan_resource_model.vlan_id)
            if numeric_vlan < allocation_range.start or numeric_vlan > allocation_range.end:
                raise ValueError("VLAN Id is outside of the allocated range {0}".format(
                    self.vlan_resource_model.allocation_range))

    def is_vlan_id_range(self):
        return self.vlan_resource_model.vlan_id.find('-') > 0

    def is_vlan_resolved(self):
        return self.vlan_resource_model.virtual_network

    def get_vlan_range_from_vlan_id(self):
        range_arr = self.vlan_resource_model.vlan_id.split("-", 2)
        return self.VlanRange(range_arr[0], range_arr[1])

    def get_allocation_range(self):
        range_arr = self.vlan_resource_model.allocation_range.split("-", 2)
        return self.VlanRange(range_arr[0], range_arr[1])

    class VlanRange(object):
        """
        Inner class that represents a numeric vlan range
        """

        def __init__(self, start, end):
            self.start = start
            self.end = end
