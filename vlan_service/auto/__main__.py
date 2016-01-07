import qualipy.scripts.cloudshell_scripts_helpers as helpers
from common.model_factory import ResourceModelParser
from vlan_service.provider import VlanServiceProvider


def main():
    # get resource model
    resource_context = helpers.get_resource_context_details()
    vlan_auto_resource_model = ResourceModelParser().convert_to_resource_model(resource_context)

    vlan_id = VlanServiceProvider().resolve_vlan_auto()



if __name__ == "__main__":
    main()
