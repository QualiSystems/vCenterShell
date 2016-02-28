from multiprocessing.pool import ThreadPool

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
        if deploy_result is None:
            return

        reservation_details = api.GetReservationDetails(self.reservation_id)
        self._connect_all_routes_in_reservation(api, reservation_details)

        self._run_async_power_on_refresh_ip_install(api=api, deploy_result=deploy_result)

        logger.info("Setup for reservation {0} completed".format(self.reservation_id))

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

        endpoint = [side for endpoint in connectors for side in [endpoint.Target, endpoint.Source]]

        if not endpoints:
            logger.info("No routes to connect for reservation {0}".format(self.reservation_id))
            return

        logger.info("Executing connect routes for reservation {0}".format(self.reservation_id))

        return api.ConnectRoutesInReservation(self.reservation_id, endpoints, 'bi')

    def _run_async_power_on_refresh_ip_install(self, api, deploy_result):
        if not deploy_result.ResultItems:
            logger.info("Nothing to power on. No deployed apps found in reservation {0}".format(self.reservation_id))
            return None

        pool = ThreadPool(len(deploy_result.ResultItems))

        for resultItem in deploy_result.ResultItems:
            if resultItem.Success:
                pool.apply_async(self._power_on_refresh_ip_install, (api, resultItem))

        else:
            logger.info("Failed to deploy app {0} in reservation {1}. Error: {2}."
                        .format(resultItem.AppName, self.reservation_id, resultItem.Error))

        pool.close()
        pool.join()

    def _power_on_refresh_ip_install(self, api, deployed_app):
        deployed_app = deployed_app
        deployed_app_name = deployed_app.AppDeploymentyInfo.LogicalResourceName

        try:
            logger.info("Executing 'Power On' on deployed app {0} in reservation {1}"
                        .format(deployed_app_name, self.reservation_id))
            api.ExecuteResourceConnectedCommand(self.reservation_id, deployed_app_name, "PowerOn", "power")
            api.SetResourceLiveStatus(deployed_app_name, "Online", "Active")
        except Exception as exc:
            logger.error("Error powering on deployed app {0} in reservation {1}. Error: {2}"
                         .format(deployed_app_name, self.reservation_id, str(exc)))
            return False

        try:
            logger.info("Executing 'Refresh IP' on deployed app {0} in reservation {1}"
                        .format(deployed_app_name, self.reservation_id))
            api.ExecuteResourceConnectedCommand(self.reservation_id, deployed_app_name, "remote_refresh_ip",
                                                "remote_connectivity")
        except Exception as exc:
            logger.error("Error refreshing IP on deployed app {0} in reservation {1}. Error: {2}"
                         .format(deployed_app_name, self.reservation_id, str(exc)))
            return False

        try:
            installation_info = deployed_app.AppInstallationInfo
            if installation_info:
                logger.info("Executing installation script {0} on deployed app {1} in reservation {2}"
                            .format(installation_info.ScriptCommandName, deployed_app_name, self.reservation_id))

                script_inputs = []
                for installation_script_input in installation_info.ScriptInputs:
                    script_inputs.append(
                            InputNameValue(installation_script_input["name"], installation_script_input["value"]))

                installation_result = api.ExecuteInstallAppCommand(self.reservation_id, deployed_app_name,
                                                                   installation_info.ScriptCommandName, script_inputs)
                logger.debug("Installation_result: " + installation_result.Output)
        except Exception as exc:
            logger.error("Error installing deployed app {0} in reservation {1}. Error: {2}"
                         .format(deployed_app_name, self.reservation_id, str(exc)))
            return False

        return True
