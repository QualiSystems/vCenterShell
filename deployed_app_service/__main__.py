import qualipy.scripts.cloudshell_scripts_helpers as helpers

from common.model_factory import ResourceModelParser
from deployed_app_service.connect import DeployedAppService


def main():
    resource_model_parser = ResourceModelParser()
    deployed_app_service = DeployedAppService(resource_model_parser)
    vlan_spec_type = helpers.get_user_param('VLAN_SPEC_TYPE')
    vlan_id = helpers.get_user_param('VLAN_ID')
    deployed_app_service.connect(vlan_spec_type, vlan_id)


if __name__ == "__main__":
    main()
