import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import *
from common.logger import getLogger

logger = getLogger("App Orchestration Driver")


def execute_app_orchestration():
    # Retrieve data from environment variables
    reservation_id = helpers.get_reservation_context_details().id
    resource_details = helpers.get_resource_context_details_dict()
    helpers.get_resource_context_details()
    app_name = resource_details["name"]
    deployment_service = resource_details["appData"]["deploymentService"]["name"]

    # Start api session
    api = helpers.get_api_session()

    # execute deploy app
    deployment_result = deploy_app(api, app_name, deployment_service, reservation_id)

    # if visual connector endpoints contains service with attribute "Virtual Network" execute connect command
    # TODO

    # logical resource execute "Power On"
    power_on_deployed_app(api, app_name, deployment_result, reservation_id)

    # if install service exists on app execute it
    # TODO

    # Set live status - deployment done
    api.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Online", "Active")

    logger.info("Deployed {0} Successfully".format(app_name))


def power_on_deployed_app(api, app_name, deployment_result, reservation_id):
    try:
        logger.info("Powering on deployed app {0}".format(deployment_result.LogicalResourceName))
        logger.debug("Powering on deployed app {0}. VM UUID: {1}".format(deployment_result.LogicalResourceName,
                                                                         deployment_result.VmUuid))
        api.ExecuteCommand(reservation_id, deployment_result.CloudProviderResourceName, "Resource", "Power On",
                           [InputNameValue("COMMAND", "power_on"), InputNameValue("VM_UUID", deployment_result.VmUuid)])
    except Exception as exc:
        logger.error("Error powering on deployed app {0}. Error: {1}".format(app_name, str(exc)))
        exit(1)


def deploy_app(api, app_name, deployment_service, reservation_id):
    try:
        logger.info("Executing '{0}' on app '{1}'...".format(deployment_service, app_name))
        return api.ExecuteDeployAppCommand(reservation_id, app_name)
    except CloudShellAPIError as exc:
        logger.error("Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml))
        exit(1)
    except Exception as exc:
        logger.error("Error deploying app {0}. Error: {1}".format(app_name, str(exc)))
        exit(1)
