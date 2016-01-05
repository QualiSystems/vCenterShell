import json
import time
import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import *

# Retrieve environment variables
reservationId = helpers.get_reservation_context_details().id
resourceDetails = helpers.get_resource_context_details()
appName = resourceDetails["name"]
deploymentService = resourceDetails["appData"]["deploymentService"]["name"]
deployed_app_family = resourceDetails["appData"]["logicalResource"]["family"]
deployed_app_model = resourceDetails["appData"]["logicalResource"]["model"]
deployed_app_driver = resourceDetails["appData"]["logicalResource"]["driver"]

# Start api session
api = helpers.get_api_session()

api.WriteMessageToReservationOutput(reservationId, "Executing '{0}' on app '{1}'...".format(deploymentService, appName))
deployment_result = None

try:
    result = api.ExecuteDeployAppCommand(reservationId, appName)
    deployment_result = json.loads(result.Output)
except CloudShellAPIError as exc:
    print "Error deploying app {0}. Error: {1}".format(appName, exc.rawxml)
    exit(1)
except Exception as exc:
    print "Error deploying app {0}. Error: {1}".format(appName, str(exc))
    exit(1)

# Get deployment result data
vm_name = deployment_result["vm_name"]
vm_path = deployment_result["vm_path"]
uuid = deployment_result["uuid"]

# Get App layout positions
X = 0
Y = 0
positions = api.GetReservationServicesPositions(reservationId)
for resourcePosition in positions.ResourceDiagramLayouts:
    if resourcePosition.ResourceName == appName:
        X = resourcePosition.X
        Y = resourcePosition.Y

# Get connected resources to app
connectedResources = []
connectors = api.GetReservationDetails(reservationId).ReservationDescription.Connectors
for connector in connectors:
    if connector.Source == appName:
        connectedResources.append(connector.Target)
    elif connector.Target == appName:
        connectedResources.append(connector.Source)

# Create deployed app logical resource
deployed_app_resource = None
try:
    deployed_app_resource = api.CreateResource(deployed_app_family, deployed_app_model, vm_name, uuid)
    api.SetAttributesValues(
            [ResourceAttributesUpdateRequest(deployed_app_resource.Name,
                                             [AttributeNameValue("vCenter Inventory Path", vm_path),
                                              AttributeNameValue("UUID", uuid)])])
    if deployed_app_driver:
        api.UpdateResourceDriver(deployed_app_resource.Name, deployed_app_driver)
except Exception, e:
    print "Error creating deployed app logical resource. Please note that virtual machine '{0}' was created. " \
          "Error: {1}"\
        .format(vm_name, str(e))
    exit(1)

# Add logical resource to reservation
api.AddResourcesToReservation(reservationId, [deployed_app_resource.Name], False)

# Update logical resource position
api.SetReservationResourcePosition(reservationId, deployed_app_resource.Name, X, Y)

# Remove application instance
api.RemoveServicesFromReservation(reservationId, [appName])

# Set live status - deployment done
api.SetResourceLiveStatus(deployed_app_resource.Name, "Online", "Active")

api.WriteMessageToReservationOutput(reservationId, "Deployed " + appName + " Successfully")

# Set connections that were connected to the app
connectionsToRestore = []
for cr in connectedResources:
    connectionsToRestore.append(SetConnectorRequest(deployed_app_resource.Name, cr, "bi", ""))
if len(connectionsToRestore) > 0:
    api.SetConnectorsInReservation(reservationId, connectionsToRestore)

# small delay to let the diagram refresh
time.sleep(2)
