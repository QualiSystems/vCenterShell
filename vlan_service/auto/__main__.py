import os
import models
from time import sleep

import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.testshell_api import AttributeNameValue

from common.model_factory import ResourceModelParser
from vlan_service.resolver.provider import VlanResolverProvider


def main():
    # get resource model
    resource_context = helpers.get_resource_context_details()

    resource_model_parser = ResourceModelParser()
    vlan_auto_resource_model = resource_model_parser.convert_to_resource_model(resource_context)

    # get reservation details
    reservation_context = helpers.get_reservation_context_details()

    # Start api session
    api = helpers.get_api_session()

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
