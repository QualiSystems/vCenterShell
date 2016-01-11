import os

import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.testshell_api import ResourceAttributesUpdateRequest, AttributeNameValue

from models.VLANAutoResourceModel import VLANAutoResourceModel
from vlan_service.resolver.provider import VlanResolverProvider


def main():

    # get resource model
    resource_context = helpers.get_resource_context_details()

    vlan_auto_resource_model = VLANAutoResourceModel()
    vlan_auto_resource_model.access_mode = resource_context.attributes["Access Mode"]
    vlan_auto_resource_model.allocation_ranges = resource_context.attributes["Allocation Ranges"]
    vlan_auto_resource_model.isolation_level = resource_context.attributes["Isolation Level"]
    vlan_auto_resource_model.vlan_id = resource_context.attributes["VLAN Id"]
    vlan_auto_resource_model.virtual_network = resource_context.attributes["Virtual Network"]
    vlan_auto_resource_model.virtual_network_attribute = "Virtual Network"

    # get reservation details
    reservation_context = helpers.get_reservation_context_details()

    # Start api session
    api = helpers.get_api_session()

    api.WriteMessageToReservationOutput(reservation_context.id, os.environ["reservationContext".upper()])

    #reservation_details = api.GetReservationDetails(reservation_context.id)


    vlan_service_provider = VlanResolverProvider(vlan_resource_model=vlan_auto_resource_model,
                                                 pool_id=reservation_context.domain,
                                                 reservation_id=reservation_context.id,
                                                 owner_id=resource_context.name,
                                                 api=api)

    if not vlan_service_provider.is_vlan_resolved():
        # resolve vlan id
        vlan_id = vlan_service_provider.resolve_vlan_auto()
        # set resolved vlan id to virtual network attribute
        api.SetServiceAttributesValues(reservation_context.id,
                                       resource_context.name,
                                       [AttributeNameValue(
                                               vlan_auto_resource_model.virtual_network_attribute,
                                               vlan_id)])
        # write success message to reservation output
        api.WriteMessageToReservationOutput(reservation_context.id,
                                            "{0} resolved vlan id {1} successfully".format(resource_context.name,
                                                                                           str(vlan_id)))
    else:
        # write already resolved message to reservation output
        api.WriteMessageToReservationOutput(reservation_context.id,
                                            "{0} already has a resolved vlan id: {1}"
                                            .format(resource_context.name,
                                                    str(vlan_auto_resource_model.virtual_network)))


if __name__ == "__main__":
    main()
