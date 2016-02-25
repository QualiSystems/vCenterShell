import threading

import cloudshell.api.cloudshell_scripts_helpers as helpers
from cloudshell.api.cloudshell_api import *

from common.logger import getLogger

logger = getLogger("CloudShell Sandbox Setup")


class EnvironmentSetup:
    def __init__(self):
        self.reservation_id = helpers.get_reservation_context_details().id

    def execute(self):
        api = helpers.get_api_session()
        reservation_details = api.GetReservationDetails(self.reservation_id)

        deploy_result = self._deploy_apps_in_reservation(api, reservation_details)

        reservation_details = api.GetReservationDetails(self.reservation_id)
        self._connect_all_routes_in_reservation(api, reservation_details)
        
        power_on_result = self._power_deployed_apps_and_refresh_ip(api, deploy_result)

    def _power_deployed_apps_and_refresh_ip(self, api, deploy_result):
        if not deploy_result.ResultItems:
            logger.info("No deployed apps found in reservation {0}".format(self.reservation_id))
            return None

        results_dict = dict()
        threads = []
        thread_lock = threading.Lock()

        for resultItem in deploy_result.ResultItems:
            if resultItem.Success:
                thread = PowerOnAppThread(api, self.reservation_id, results_dict, thread_lock)
                threads.append(thread)
                thread.start()
            else:
                logger.info("Failed to deploy app {0} in reservation {1}. Error: {2}."
                            .format(resultItem.AppName, self.reservation_id, resultItem.Error))

        for t in threads:
            t.join()

        return results_dict

    def _deploy_apps_in_reservation(self, api, reservation_details):
        apps = reservation_details.ReservationDescription.Apps
        if not apps:
            logger.info("No apps found in reservation {0}".format(self.reservation_id))
            return None

        app_names = map(lambda x: x.Name, apps)
        app_inputs = map(lambda x: DeployAppInput(x.Name, "Name", x.Name), apps)

        logger.info(
                "Deploying apps for reservation {0}. App names: {1}".format(reservation_details, ", ".join(app_names)))

        return api.ExecuteDeployAppCommandBulk(self.reservation_id, app_names, app_inputs)

    def _connect_all_routes_in_reservation(self, api, reservation_details):
        connectors = reservation_details.ReservationDescription.Connectors
        endpoints = []
        for endpoint in connectors:
            endpoints.append(endpoint.Target)
            endpoints.append(endpoint.Source)

        if len(endpoints) == 0:
            logger.info("No routes to connect for reservation {0}".format(self.reservation_id))
            return

        logger.info("Executing connect routes for reservation {0}".format(self.reservation_id))

        return api.ConnectRoutesInReservation(self.reservation_id, endpoints, 'bi')


class PowerOnAppThread(threading.Thread):

    def __init__(self, api, reservation_id, deployed_app_name, results_dict, results_lock):
        threading.Thread.__init__(self)
        self.api = api
        self.reservationId = reservation_id
        self.deployed_app_name = deployed_app_name
        self.results_dict = results_dict
        self.results_lock = results_lock

    def run(self):
        try:
            logger.info("Executing 'Power On' on deployed app {0} in reservation {1}"
                        .format(self.deployed_app_name, self.reservation_id))
            self.api.ExecuteResourceConnectedCommand(self.deployed_app_name, self.reservationId, "PowerOn", "power")
        except Exception as exc:
            logger.error("Error powering on deployed app {0} in reservation {1}. Error: {2}"
                         .format(self.deployed_app_name, self.reservationId, str(exc)))
            self._set_result(False)
            return

        try:
            logger.info("Executing 'Refresh IP' on deployed app {0} in reservation {1}"
                        .format(self.deployed_app_name, self.reservation_id))
            self.api.ExecuteResourceConnectedCommand(self.deployed_app_name, self.reservationId, "remote_refresh_ip",
                                                     "remote_connectivity")
        except Exception as exc:
            logger.error("Error refreshing IP on deployed app {0} in reservation {1}. Error: {2}"
                         .format(self.deployed_app_name, self.reservationId, str(exc)))
            self._set_result(False)
            return

        self._set_result(True)

    def _set_result(self, success):
        self.results_lock.acquire()
        self.results_dict[self.deployed_app_name] = success
        self.results_lock.release()



