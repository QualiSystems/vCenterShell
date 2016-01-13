import time
import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import *


# TODO add logger

def main():
    # Retrieve data from environment variables
    reservation_id = helpers.get_reservation_context_details().id
    resource_details = helpers.get_resource_context_details_dict()
    app_name = resource_details["name"]
    deployment_service = resource_details["appData"]["deploymentService"]["name"]

    # Start api session
    api = helpers.get_api_session()

    api.WriteMessageToReservationOutput(reservation_id,
                                        "Executing '{0}' on app '{1}'...".format(deployment_service, app_name))

    deployment_result = deploy_app(api, app_name, reservation_id)

    # if visual connector endpoints contains service with attribute "Virtual Network" execute connect command
    # TODO

    # logical resource execute "Power On"
    api.ExecuteCommand(reservation_id, deployment_result.CloudProviderResourceName, "Resource", "Power On",
                       [InputNameValue("COMMAND", "power_on"), InputNameValue("VM_UUID", deployment_result.VmUuid)])

    # if install service exists on app execute it
    # TODO

    # Set live status - deployment done
    api.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Online", "Active")
    api.WriteMessageToReservationOutput(reservation_id, "Deployed " + app_name + " Successfully")

    # small delay to let the diagram refresh
    time.sleep(2)


def deploy_app(api, app_name, reservation_id):
    try:
        return api.ExecuteDeployAppCommand(reservation_id, app_name)
    except CloudShellAPIError as exc:
        print "Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml)
        exit(1)
    except Exception as exc:
        print "Error deploying app {0}. Error: {1}".format(app_name, str(exc))
        exit(1)


if __name__ == "__main__":
    main()
