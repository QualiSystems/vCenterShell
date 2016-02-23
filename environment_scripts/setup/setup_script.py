import cloudshell.api.cloudshell_scripts_helpers as helpers
from cloudshell.api.cloudshell_api import *

from common.logger import getLogger

logger = getLogger("App Orchestration Driver")

api = helpers.get_api_session()
reservation_id = helpers.get_reservation_context_details().id
reservation_detailes = api.GetReservationDetails(reservation_id)


def execute_environment_setup():
    deploy_result = _deploy_apps_in_reservation()

    if deploy_result:
        connect_result = _connect_all_routes_in_reservation()

        power_on_result = _power_apps_in_reservation()


def _power_apps_in_reservation():
    apps = reservation_detailes.ReservationDescription.Apps
    if not apps:
        logger.info("No apps found in reservation {0}".format(reservation_id))
        return None

    for app in apps:
        return api.ExecuteResourceCommand(reservation_id, 'vCenert', 'PowerOn')


def _deploy_apps_in_reservation():
    apps = reservation_detailes.ReservationDescription.Apps
    if not apps:
        logger.info("No apps found in reservation {0}".format(reservation_id))
        return None

    app_names = map(lambda x: x.Name, apps)
    app_inputs = map(lambda x: DeployAppInput(x.Name, "Name", x.Name), apps)

    logger.info("deploying apps for reservation {0}, name:{1}".format(reservation_detailes, app_names))

    result = api.ExecuteDeployAppCommandBulk(reservation_id, app_names, app_inputs)
    return result


def _connect_all_routes_in_reservation():
    connectors = [connector for connector in reservation_detailes.ReservationDescription.Connectors]

    endpoints = []
    for endpoint in connectors:
        endpoints.append(endpoint.Target)
        endpoints.append(endpoint.Source)

    if len(endpoints) == 0:
        logger.info("No routes to connect for reservation {0}".format(reservation_id))
        return

    logger.info("Executing connect for reservation {0}".format(reservation_id))
    return api.ConnectRoutesInReservation(reservation_id, endpoints, 'bi')
