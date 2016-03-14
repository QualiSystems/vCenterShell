from multiprocessing.pool import ThreadPool

import cProfile
import pstats
import datetime
import cloudshell.api.cloudshell_scripts_helpers as helpers
from cloudshell.api.cloudshell_api import *
from cloudshell.core.logger import qs_logger

def get_vm_custom_param(vm_custom_params, param_name):
    """
    :param list[VmCustomParam] vm_custom_params:
    :param param_name:
    :return:
    """
    for param in vm_custom_params:
        if param.Name == param_name:
            return param
    return None

### util methods to help us benchmark the application ###

### http://stackoverflow.com/questions/5375624/a-decorator-that-profiles-a-method-call-and-logs-the-profiling-result ###
def profileit(name):
    def inner(func):
        def wrapper(*args, **kwargs):
            prof = cProfile.Profile()
            retval = prof.runcall(func, *args, **kwargs)
            s = open(r"//qsnas1/shared/vcentershell_profiling/" + name + "_" + str(datetime.datetime.now()).replace(':', '_') + ".text", 'w')
            stats = pstats.Stats(prof, stream=s)
            stats.strip_dirs().sort_stats('cumtime').print_stats()
            return retval
        return wrapper
    return inner


class EnvironmentSetup:
    def __init__(self):
        self.reservation_id = helpers.get_reservation_context_details().id
        self.logger = qs_logger.get_qs_logger(name="CloudShell Sandbox Setup",reservation_id=self.reservation_id)

    @profileit(name='CloudShell_Sandbox_Setup')
    def execute(self):
        api = helpers.get_api_session()
        reservation_details = api.GetReservationDetails(self.reservation_id)

        deploy_result = self._deploy_apps_in_reservation(api, reservation_details)
        if deploy_result is None:
            return

        reservation_details = api.GetReservationDetails(self.reservation_id)
        self._connect_all_routes_in_reservation(api, reservation_details)

        self._run_async_power_on_refresh_ip_install(api=api, deploy_result=deploy_result)

        self.logger.info("Setup for reservation {0} completed".format(self.reservation_id))

    def _deploy_apps_in_reservation(self, api, reservation_details):
        apps = reservation_details.ReservationDescription.Apps
        if not apps:
            self.logger.info("No apps found in reservation {0}".format(self.reservation_id))
            return None

        app_names = map(lambda x: x.Name, apps)
        app_inputs = map(lambda x: DeployAppInput(x.Name, "Name", x.Name), apps)

        self.logger.info(
            "Deploying apps for reservation {0}. App names: {1}".format(reservation_details, ", ".join(app_names)))

        return api.DeployAppToCloudProviderBulk(self.reservation_id, app_names, app_inputs)

    def _connect_all_routes_in_reservation(self, api, reservation_details):
        connectors = reservation_details.ReservationDescription.Connectors
        endpoints = []
        for endpoint in connectors:
            if endpoint.Target and endpoint.Source:
                endpoints.append(endpoint.Target)
                endpoints.append(endpoint.Source)

        if not endpoints:
            self.logger.info("No routes to connect for reservation {0}".format(self.reservation_id))
            return

        self.logger.info("Executing connect routes for reservation {0}".format(self.reservation_id))
        self.logger.debug("Connecting: {0}".format(",".join(endpoints)))

        return api.ConnectRoutesInReservation(self.reservation_id, endpoints, 'bi')

    def _run_async_power_on_refresh_ip_install(self, api, deploy_result):
        if not deploy_result.ResultItems:
            self.logger.info("Nothing to power on. No deployed apps found in reservation {0}".format(self.reservation_id))
            return None

        pool = ThreadPool(len(deploy_result.ResultItems))

        for resultItem in deploy_result.ResultItems:
            if resultItem.Success:
                pool.apply_async(self._power_on_refresh_ip_install, (api, resultItem))
            else:
                self.logger.info("Failed to deploy app {0} in reservation {1}. Error: {2}."
                            .format(resultItem.AppName, self.reservation_id, resultItem.Error))

        pool.close()
        pool.join()

    def _power_on_refresh_ip_install(self, api, deployed_app):
        """
        :param CloudShellAPISession api:
        :param deployed_app:
        :return:
        """
        deployed_app = deployed_app
        deployed_app_name = deployed_app.AppDeploymentyInfo.LogicalResourceName

        power_on = "true"
        wait_for_ip = "true"

        try:
            self.logger.info("Getting resource details for deployed app {0} in reservation {1}"
                        .format(deployed_app_name, self.reservation_id))
            resource_details = api.GetResourceDetails(deployed_app_name)
            auto_power_on_param = get_vm_custom_param(resource_details.VmDetails.VmCustomParams, "auto_power_on")
            if auto_power_on_param:
                power_on = auto_power_on_param.Value
            wait_for_ip_param = get_vm_custom_param(resource_details.VmDetails.VmCustomParams, "wait_for_ip")
            if wait_for_ip_param:
                wait_for_ip = wait_for_ip_param.Value
        except Exception as exc:
            self.logger.error("Error getting resource details for deployed app {0} in reservation {1}. "
                         "Will use default settings. Error: {2}".format(deployed_app_name, self.reservation_id, str(exc)))

        try:
            if power_on.lower() == "true":
                self.logger.info("Executing 'Power On' on deployed app {0} in reservation {1}"
                            .format(deployed_app_name, self.reservation_id))
                api.ExecuteResourceConnectedCommand(self.reservation_id, deployed_app_name, "PowerOn", "power")
                api.SetResourceLiveStatus(deployed_app_name, "Online", "Active")
            else:
                self.logger.info("Auto Power On is off for deployed app {0} in reservation {1}"
                            .format(deployed_app_name, self.reservation_id))
        except Exception as exc:
            self.logger.error("Error powering on deployed app {0} in reservation {1}. Error: {2}"
                         .format(deployed_app_name, self.reservation_id, str(exc)))
            return False

        try:
            if wait_for_ip.lower() == "true":
                self.logger.info("Executing 'Refresh IP' on deployed app {0} in reservation {1}"
                            .format(deployed_app_name, self.reservation_id))
                api.ExecuteResourceConnectedCommand(self.reservation_id, deployed_app_name, "remote_refresh_ip",
                                                    "remote_connectivity")
            else:
                self.logger.info("Wait For IP is off for deployed app {0} in reservation {1}"
                            .format(deployed_app_name, self.reservation_id))
        except Exception as exc:
            self.logger.error("Error refreshing IP on deployed app {0} in reservation {1}. Error: {2}"
                         .format(deployed_app_name, self.reservation_id, str(exc)))
            return False

        try:
            installation_info = deployed_app.AppInstallationInfo
            if installation_info:
                self.logger.info("Executing installation script {0} on deployed app {1} in reservation {2}"
                            .format(installation_info.ScriptCommandName, deployed_app_name, self.reservation_id))

                script_inputs = []
                for installation_script_input in installation_info.ScriptInputs:
                    script_inputs.append(
                        InputNameValue(installation_script_input.Name, installation_script_input.Value))

                installation_result = api.InstallApp(self.reservation_id, deployed_app_name,
                                                     installation_info.ScriptCommandName, script_inputs)
                self.logger.debug("Installation_result: " + installation_result.Output)
        except Exception as exc:
            self.logger.error("Error installing deployed app {0} in reservation {1}. Error: {2}"
                         .format(deployed_app_name, self.reservation_id, str(exc)))
            return False

        return True
