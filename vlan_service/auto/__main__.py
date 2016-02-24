import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import AttributeNameValue
from common.model_factory import ResourceModelParser
from models import VLANAutoResourceModel
from vlan_service.resolver.provider import VlanResolverProvider
from common.utilites.command_result import set_command_result
from common.logger import getLogger

_logger = getLogger('VlanAuto')


def main():
    # get vlan auto resource model
    resource_context = helpers.get_resource_context_details()
    resource_model_parser = ResourceModelParser()
    vlan_auto_resource_model = resource_model_parser.convert_to_resource_model(resource_context, VLANAutoResourceModel)
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
        vlan_id = str(vlan_id)
        # set resolved vlan id to virtual network attribute
        api.SetServiceAttributesValues(reservation_context.id,
                                       resource_context.name,
                                       [AttributeNameValue(
                                               vlan_auto_resource_model.virtual_network_attribute,
                                               vlan_id)])
        _logger.info("{0} resolved vlan id {1} successfully".format(resource_context.name, vlan_id))

    else:
        vlan_id = str(vlan_auto_resource_model.virtual_network)
        _logger.info("{0} already has a resolved vlan id: {1}".format(resource_context.name, vlan_id))

    # command result for programmatic use
    set_command_result(vlan_id)


if __name__ == "__main__":
    main()
