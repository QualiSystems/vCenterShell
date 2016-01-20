import os
from unittest import TestCase
import qualipy.scripts.cloudshell_scripts_helpers as helpers
from models.VLANAutoResourceModel import VLANAutoResourceModel
from vlan_service.resolver.provider import VlanResolverProvider
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers

class TestVlanResolverProvider(TestCase):
    def integrationtest_get_auto_vlan_specific_id(self):

        dev_helpers.attach_to_cloudshell_as("admin", "admin", "Global", "4255fc8b-f964-444d-aa0c-96ae58659a52")

        requested_vlan_id = "24"
        os.environ["RESOURCECONTEXT"] = \
            '{' \
            ' "name":"VLAN Auto", ' \
            ' "address":"Service",' \
            ' "model":"VLAN Auto", ' \
            ' "family":"Virtual Network", ' \
            ' "description":"", ' \
            ' "fullname":"", ' \
            ' "attributes":{"Access Mode":"trunk",' \
                            '"Allocation Ranges":"2-4098",' \
                            '"Isolation Level":"Shared", ' \
                            '"Virtual Network":"", ' \
                            '"VLAN Id":"' + requested_vlan_id + '"}}'

        resource_context = helpers.get_resource_context_details()

        vlan_auto_resource_model = VLANAutoResourceModel()
        vlan_auto_resource_model.access_mode = resource_context.attributes["Access Mode"]
        vlan_auto_resource_model.allocation_ranges = resource_context.attributes["Allocation Ranges"]
        vlan_auto_resource_model.isolation_level = resource_context.attributes["Isolation Level"]
        vlan_auto_resource_model.vlan_id = resource_context.attributes["VLAN Id"]
        vlan_auto_resource_model.virtual_network = resource_context.attributes["Virtual Network"]
        vlan_auto_resource_model.virtual_network_attribute = "Virtual Network"

        # get reservation details
        reservation_details = helpers.get_reservation_context_details()

        # Start api session
        api = helpers.get_api_session()

        vlan_service_provider = VlanResolverProvider(vlan_auto_resource_model,
                                                     reservation_details.domain,
                                                     reservation_details.id,
                                                     resource_context.name,
                                                     api)
        vlan_id = vlan_service_provider.resolve_vlan_auto()

        assert(vlan_id, requested_vlan_id)

    def integrationtest_get_auto_vlan_specific_id(self):

        dev_helpers.attach_to_cloudshell_as("admin", "admin", "Global", "46d5ebc4-3903-45ab-857a-77de3f5ab8de")

        requested_vlan_id = "40-50"
        os.environ["RESOURCECONTEXT"] = \
            '{' \
            ' "name":"VLAN Auto", ' \
            ' "address":"Service",' \
            ' "model":"VLAN Auto", ' \
            ' "family":"Virtual Network", ' \
            ' "description":"", ' \
            ' "fullname":"", ' \
            ' "attributes":{"Access Mode":"trunk",' \
                            '"Allocation Ranges":"2-4098",' \
                            '"Isolation Level":"Shared", ' \
                            '"Virtual Network":"", ' \
                            '"VLAN Id":"' + requested_vlan_id + '"}}'

        resource_context = helpers.get_resource_context_details()

        vlan_auto_resource_model = VLANAutoResourceModel()
        vlan_auto_resource_model.access_mode = resource_context.attributes["Access Mode"]
        vlan_auto_resource_model.allocation_ranges = resource_context.attributes["Allocation Ranges"]
        vlan_auto_resource_model.isolation_level = resource_context.attributes["Isolation Level"]
        vlan_auto_resource_model.vlan_id = resource_context.attributes["VLAN Id"]
        vlan_auto_resource_model.virtual_network = resource_context.attributes["Virtual Network"]
        vlan_auto_resource_model.virtual_network_attribute = "Virtual Network"

        # get reservation details
        reservation_details = helpers.get_reservation_context_details()

        # Start api session
        api = helpers.get_api_session()

        vlan_service_provider = VlanResolverProvider(vlan_auto_resource_model,
                                                     reservation_details.domain,
                                                     reservation_details.id,
                                                     resource_context.name,
                                                     api)
        vlan_id = vlan_service_provider.resolve_vlan_auto()

        assert(vlan_id, "40")
