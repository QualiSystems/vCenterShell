from multiprocessing.pool import ThreadPool
import cloudshell.api.cloudshell_scripts_helpers as helpers
from cloudshell.api.cloudshell_api import *
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.core.logger import qs_logger

from environment_scripts.helpers.vm_details_helper import get_vm_custom_param
from environment_scripts.profiler.env_profiler import profileit


class EnvironmentSetup:
    def __init__(self):
        self.reservation_id = helpers.get_reservation_context_details().id
        self.logger = qs_logger.get_qs_logger(name="CloudShell Sandbox Setup", reservation_id=self.reservation_id)

    @profileit(scriptName='Setup')
    def execute(self):
        api = helpers.get_api_session()
        resource_details_cache = {}

        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='[Beginning reservation setup]')

        reservation_details = api.GetReservationDetails(self.reservation_id)

        deploy_result = self._deploy_apps_in_reservation(api=api,
                                                         reservation_details=reservation_details)

        # refresh reservation_details after app deployment if any deployed apps
        if deploy_result and deploy_result.ResultItems:
            reservation_details = api.GetReservationDetails(self.reservation_id)

        self._try_exeucte_autoload(api=api,
                                   reservation_details=reservation_details,
                                   deploy_result=deploy_result,
                                   resource_details_cache=resource_details_cache)

        self._connect_all_routes_in_reservation(api=api,
                                                reservation_details=reservation_details)

        self._run_async_power_on_refresh_ip_install(api=api,
                                                    reservation_details=reservation_details,
                                                    deploy_result=deploy_result,
                                                    resource_details_cache=resource_details_cache)

        self.logger.info("Setup for reservation {0} completed".format(self.reservation_id))
        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='[Reservation setup finished successfully]')

    def _try_exeucte_autoload(self, api, reservation_details, deploy_result, resource_details_cache):
        """
        :param GetReservationDescriptionResponseInfo reservation_details:
        :param CloudShellAPISession api:
        :param BulkAppDeploymentyInfo deploy_result:
        :param (dict of str: ResourceInfo) resource_details_cache:
        :return:
        """

        if deploy_result is None:
            return

        reservation_id = reservation_details.ReservationDescription.Id

        for deployed_app in deploy_result.ResultItems:
            deployed_app_name = deployed_app.AppDeploymentyInfo.LogicalResourceName

            api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                message='[{0}] discovery started'.format(deployed_app_name))

            resource_details = api.GetResourceDetails(deployed_app_name)
            resource_details_cache[deployed_app_name] = resource_details

            autoload = "true"
            autoload_param = get_vm_custom_param(resource_details.VmDetails.VmCustomParams, "autoload")
            if autoload_param:
                autoload = autoload_param.Value
            if autoload.lower() != "true":
                continue

            try:
                self.logger.info("Executing Autoload command on deployed app {0}".format(deployed_app_name))
                api.AutoLoad(deployed_app_name)

                api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                    message='[{0}] discovery ended successfully'.format(
                                                            deployed_app_name))
            except CloudShellAPIError as exc:
                self.logger.error(
                        "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name,
                                                                                                  exc.rawxml))
            except Exception as exc:
                self.logger.error(
                        "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name,
                                                                                                  str(exc)))

    def _deploy_apps_in_reservation(self, api, reservation_details):
        apps = reservation_details.ReservationDescription.Apps
        if not apps:
            self.logger.info("No apps found in reservation {0}".format(self.reservation_id))
            return None

        app_names = map(lambda x: x.Name, apps)
        app_inputs = map(lambda x: DeployAppInput(x.Name, "Name", x.Name), apps)

        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='[Deploying apps] {0}'.format(app_names))
        self.logger.info(
                "Deploying apps for reservation {0}. App names: {1}".format(reservation_details, ", ".join(app_names)))

        res = api.DeployAppToCloudProviderBulk(self.reservation_id, app_names, app_inputs)

        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='[Deployed all apps]')
        return res

    def _connect_all_routes_in_reservation(self, api, reservation_details):
        connectors = reservation_details.ReservationDescription.Connectors
        endpoints = []
        for endpoint in connectors:
            if endpoint.Target and endpoint.Source:
                endpoints.append(endpoint.Target)
                endpoints.append(endpoint.Source)

        if not endpoints:
            self.logger.info("No routes to connect for reservation {0}".format(self.reservation_id))
            api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                message='[No routes to connect]')
            return

        self.logger.info("Executing connect routes for reservation {0}".format(self.reservation_id))
        self.logger.debug("Connecting: {0}".format(",".join(endpoints)))

        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='[Start connecting all routes in reservation]')

        res = api.ConnectRoutesInReservation(self.reservation_id, endpoints, 'bi')
        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='[Done connecting all routes in reservation]')
        return res

    def _run_async_power_on_refresh_ip_install(self, api, reservation_details, deploy_result, resource_details_cache):
        """
        :param CloudShellAPISession api:
        :param GetReservationDescriptionResponseInfo reservation_details:
        :param BulkAppDeploymentyInfo deploy_result:
        :param (dict of str: ResourceInfo) resource_details_cache:
        :return:
        """
        resources = reservation_details.ReservationDescription.Resources
        pool = ThreadPool(len(resources))

        for resource in resources:
            pool.apply_async(self._power_on_refresh_ip_install, (api, resource, deploy_result, resource_details_cache))

        pool.close()
        pool.join()

    def _power_on_refresh_ip_install(self, api, resource, deploy_result, resource_details_cache):
        """
        :param CloudShellAPISession api:
        :param ReservedResourceInfo resource:
        :param BulkAppDeploymentyInfo deploy_result:
        :param (dict of str: ResourceInfo) resource_details_cache:
        :return:
        """

        deployed_app_name = resource.Name
        deployed_app_data = None

        power_on = "true"
        wait_for_ip = "true"

        try:
            self.logger.debug("Getting resource details for resource {0} in reservation {1}"
                              .format(deployed_app_name, self.reservation_id))

            if deployed_app_name in resource_details_cache:
                resource_details = resource_details_cache[deployed_app_name]
            else:
                resource_details = api.GetResourceDetails(deployed_app_name)

            # check if deployed app
            if not resource_details.VmDetails:
                self.logger.debug("Resource {0} is not a deployed app, nothing to do with it".format(deployed_app_name))
                return True

            auto_power_on_param = get_vm_custom_param(resource_details.VmDetails.VmCustomParams, "auto_power_on")
            if auto_power_on_param:
                power_on = auto_power_on_param.Value
            wait_for_ip_param = get_vm_custom_param(resource_details.VmDetails.VmCustomParams, "wait_for_ip")
            if wait_for_ip_param:
                wait_for_ip = wait_for_ip_param.Value

            # check if we have deployment data
            if deploy_result is not None:
                for data in deploy_result.ResultItems:
                    if data.Success and data.AppDeploymentyInfo.LogicalResourceName == deployed_app_name:
                        deployed_app_data = data
        except Exception as exc:
            self.logger.error("Error getting resource details for deployed app {0} in reservation {1}. "
                              "Will use default settings. Error: {2}".format(deployed_app_name, self.reservation_id,
                                                                             str(exc)))

        try:
            self._power_on(api, deployed_app_name, power_on)
        except Exception as exc:
            self.logger.error("Error powering on deployed app {0} in reservation {1}. Error: {2}"
                              .format(deployed_app_name, self.reservation_id, str(exc)))
            return False

        try:
            self._wait_for_ip(api, deployed_app_name, wait_for_ip)
        except Exception as exc:
            self.logger.error("Error refreshing IP on deployed app {0} in reservation {1}. Error: {2}"
                              .format(deployed_app_name, self.reservation_id, str(exc)))
            return False

        try:
            self._install(api, deployed_app_data, deployed_app_name)
        except Exception as exc:
            self.logger.error("Error installing deployed app {0} in reservation {1}. Error: {2}"
                              .format(deployed_app_name, self.reservation_id, str(exc)))
            return False

        return True

    def _install(self, api, deployed_app_data, deployed_app_name):
        installation_info = None
        if deployed_app_data:
            installation_info = deployed_app_data.AppInstallationInfo
        else:
            self.logger.info("Cant execute installation script for deployed app {0} - No deployment data"
                             .format(deployed_app_name))
        if installation_info:
            self.logger.info("Executing installation script {0} on deployed app {1} in reservation {2}"
                             .format(installation_info.ScriptCommandName, deployed_app_name, self.reservation_id))
            api.WriteMessageToReservationOutput(
                    reservationId=self.reservation_id,
                    message='[{0}] installation started'.format(deployed_app_name))
            script_inputs = []
            for installation_script_input in installation_info.ScriptInputs:
                script_inputs.append(
                        InputNameValue(installation_script_input.Name, installation_script_input.Value))

            installation_result = api.InstallApp(self.reservation_id, deployed_app_name,
                                                 installation_info.ScriptCommandName, script_inputs)
            api.WriteMessageToReservationOutput(
                    reservationId=self.reservation_id,
                    message='[{0}] installation ended successfully'.format(deployed_app_name))

            self.logger.debug("Installation_result: " + installation_result.Output)

    def _wait_for_ip(self, api, deployed_app_name, wait_for_ip):
        if wait_for_ip.lower() == "true":
            self.logger.info("Executing 'Refresh IP' on deployed app {0} in reservation {1}"
                             .format(deployed_app_name, self.reservation_id))
            api.WriteMessageToReservationOutput(
                    reservationId=self.reservation_id,
                    message='[{0}] is waiting for IP address, this may take a while'.format(deployed_app_name))

            ip = api.ExecuteResourceConnectedCommand(self.reservation_id, deployed_app_name,
                                                     "remote_refresh_ip",
                                                     "remote_connectivity")
            if ip and hasattr(ip, 'Output'):
                ip = ip.Output.replace('command_json_result="', '').replace('"=command_json_result_end', '')
                api.WriteMessageToReservationOutput(
                        reservationId=self.reservation_id,
                        message='[{0}] {1}'.format(
                                deployed_app_name,
                                'IP address is [{0}]'.format(ip) if ip else 'IP address not found'))
        else:
            self.logger.info("Wait For IP is off for deployed app {0} in reservation {1}"
                             .format(deployed_app_name, self.reservation_id))

    def _power_on(self, api, deployed_app_name, power_on):
        if power_on.lower() == "true":
            self.logger.info("Executing 'Power On' on deployed app {0} in reservation {1}"
                             .format(deployed_app_name, self.reservation_id))
            api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                message='[{0}] is powering on'.format(deployed_app_name))
            api.ExecuteResourceConnectedCommand(self.reservation_id, deployed_app_name, "PowerOn", "power")
            api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                message='[{0}] powered on'.format(deployed_app_name))
            api.SetResourceLiveStatus(deployed_app_name, "Online", "Active")
        else:
            self.logger.info("Auto Power On is off for deployed app {0} in reservation {1}"
                             .format(deployed_app_name, self.reservation_id))
