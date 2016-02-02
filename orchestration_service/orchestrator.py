import qualipy.scripts.cloudshell_scripts_helpers as helpers
import time
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
    installation_service_data = resource_details["appData"]["installationService"]

    time.sleep(20)
    # Start api session
    api = helpers.get_api_session()

    # execute deploy app
    deployment_result = deploy_app(api, app_name, deployment_service, reservation_id)

    # if visual connector endpoints contains service with attribute "Virtual Network" execute connect command
    # TODO

    # TODO this is temporary until we move to drivers
    api.SetAttributesValues(
            [ResourceAttributesUpdateRequest(
                    deployment_result.LogicalResourceName,
                    [AttributeNameValue("VM_UUID", deployment_result.VmUuid),
                     AttributeNameValue("Cloud Provider", deployment_result.CloudProviderResourceName)])])

    # connect all
    connect_all(api, reservation_id)

    # "Power On"
    power_on_deployed_app(api, app_name, deployment_result, reservation_id)

    # if install service exists on app execute it
    execute_installation_if_exist(api, deployment_result, installation_service_data, reservation_id)

    # refresh ip
    #refresh_ip(api, deployment_result, reservation_id)

    # Set live status - deployment done
    api.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Online", "Active")

    logger.info("Deployed {0} Successfully".format(app_name))


def connect_all(api, reservation_id):
    try:
        api.ExecuteEnvironmentCommand(reservation_id, "Connect All")
    except CloudShellAPIError as exc:
        logger.error("Error executing connect all. Error: {0}".format(exc.rawxml))
        exit(1)
    except Exception as exc:
        logger.error("Error executing connect all. Error: {0}".format(str(exc)))
        exit(1)


def refresh_ip(api, deployment_result, reservation_id):
    logger.info("Waiting to get IP for deployed app resource {0}...".format(deployment_result.LogicalResourceName))
    try:
        # TODO update the script inputs with data from the installation service
        api.ExecuteCommand(reservation_id, deployment_result.CloudProviderResourceName,
                           "Resource" "refresh_ip", [InputNameValue('vm_uuid',
                                                                    deployment_result.VmUuid),
                                                     InputNameValue('resource_name',
                                                                    deployment_result.LogicalResourceName)])
    except CloudShellAPIError as exc:
        logger.error("Error refreshing ip for deployed app {0}. Error: {1}"
                     .format(deployment_result.LogicalResourceName, exc.rawxml))
        exit(1)
    except Exception as exc:
        logger.error("Error refreshing ip for deployed app {0}. Error: {1}"
                     .format(deployment_result.LogicalResourceName, str(exc)))
        exit(1)


def execute_installation_if_exist(api, deployment_result, installation_service_data, reservation_id):
    if not installation_service_data:
        return
    installation_service_name = installation_service_data["name"]
    logger.info("Executing installation '{0}' on deployed app resource '{1}'..."
                .format(installation_service_name, deployment_result.LogicalResourceName))
    try:
        # TODO update the script inputs with data from the installation service
        installation_result = api.ExecuteInstallAppCommand(reservation_id, deployment_result.LogicalResourceName,
                                                           "Install", [InputNameValue('STAM', "- its just a demo")])
        logger.debug("installation_result: " + installation_result.Output)
    except CloudShellAPIError as exc:
        logger.error("Error installing deployed app {0}. Error: {1}"
                     .format(deployment_result.LogicalResourceName, exc.rawxml))
        exit(1)
    except Exception as exc:
        logger.error(
                "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName, str(exc)))
        exit(1)


def power_on_deployed_app(api, app_name, deployment_result, reservation_id):
    try:
        logger.info("Powering on deployed app {0}".format(deployment_result.LogicalResourceName))
        logger.debug("Powering on deployed app {0}. VM UUID: {1}".format(deployment_result.LogicalResourceName,
                                                                         deployment_result.VmUuid))
        api.ExecuteCommand(reservation_id, deployment_result.CloudProviderResourceName, "Resource", "power_on",
                           [InputNameValue("vm_uuid", deployment_result.VmUuid),
                            InputNameValue("resource_fullname", "")])
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



