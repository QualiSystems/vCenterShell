import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import CloudShellAPISession, ReservationDiagramLayoutResponseInfo, InputNameValue
import os
import json
import random
import time
import sys
from pprint import pprint


# Retrieve environment variables
#connectivity = json.loads(os.environ["QUALICONNECTIVITY"])
reservationDetails = json.loads(os.environ["RESERVATIONCONTEXT"])
resourceDetails = json.loads(os.environ["RESOURCECONTEXT"])
reservationId = reservationDetails["id"]
appName = resourceDetails["name"]

# Start api session
api = helpers.get_api_session()

result = api.ExecuteCommand(reservationId, "vCenter", "Resource", "testScriptParams",
                            [InputNameValue("command", "myCommand"),InputNameValue("data", "my data"), ], True)
print "========================"
print "output: " + json.dumps(result.__dict__)


# appData = resourceDetails["appData"]
#deploymentService = appData['deploymentService']['name']
#api.WriteMessageToReservationOutput(reservationId, "Executing deployment service '{0}'...".format(deploymentService))

#output = api.ExecuteAppCommand(reservationId, appName, deploymentService, "Deploy")
#api.WriteMessageToReservationOutput(reservationId, "Command output: '{0}'...".format(output))

