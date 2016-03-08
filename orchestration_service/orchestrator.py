import jsonpickle
from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from common.cloud_shell.driver_helper import CloudshellDriverHelper
from common.logger import getLogger

logger = getLogger("App Orchestration Driver")


class DeployAppOrchestrationDriver(object):
    def __init__(self):
        self.cs_helper = CloudshellDriverHelper()

    def deploy(self, context):
        """
        Deploys app from template
        :type context: models.QualiDriverModels.ResourceCommandContext
        """
        reservation_id = context.reservation.reservation_id
        resource_details = context.resource
        app_name = resource_details.name
        app_data = jsonpickle.decode(resource_details.app_context.app_request_json)
        deployment_service = app_data["deploymentService"]["name"]
        installation_service_data = app_data["installationService"]

        # Start api session
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.reservation.domain)
        # execute deploy app
        deployment_result = self.deploy_app(session, app_name, deployment_service, reservation_id)

        # if visual connector endpoints contains service with attribute "Virtual Network" execute connect command
        self.connect_routes_on_deployed_app(session, reservation_id, deployment_result.LogicalResourceName)

        # "Power On"
        self.power_on_deployed_app(session, app_name, deployment_result, reservation_id)

        # refresh ip
        self.refresh_ip(session, deployment_result, reservation_id)

        # if install service exists on app execute it
        self.execute_installation_if_exist(session, deployment_result, installation_service_data, reservation_id)

        # Set live status - deployment done
        session.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Online", "Active")

        logger.info("Deployed {0} Successfully".format(deployment_result.LogicalResourceName))
        return "Deployed {0} Successfully".format(deployment_result.LogicalResourceName)

    @staticmethod
    def connect_routes_on_deployed_app(api, reservation_id, resource_name):
        try:
            reservation = api.GetReservationDetails(reservation_id)
            connectors = [connector for connector in reservation.ReservationDescription.Connectors
                          if connector.Source == resource_name or connector.Target == resource_name]
            endpoints = []
            for endpoint in connectors:
                endpoints.append(endpoint.Target)
                endpoints.append(endpoint.Source)

            if len(endpoints) == 0:
                logger.info("No routes to connect for app {0}".format(resource_name))
                return

            logger.info("Executing connect for app {0}".format(resource_name))
            api.ConnectRoutesInReservation(reservation_id, endpoints, 'bi')

        except CloudShellAPIError as exc:
            print "Error executing connect all. Error: {0}".format(exc.rawxml)
            logger.error("Error executing connect all. Error: {0}".format(exc.rawxml))
            raise exc
        except Exception as exc:
            print "Error executing connect all. Error: {0}".format(str(exc))
            logger.error("Error executing connect all. Error: {0}".format(str(exc)))
            raise exc

    @staticmethod
    def refresh_ip(api, deployment_result, reservation_id):
        logger.info("Waiting to get IP for deployed app resource {0}...".format(deployment_result.LogicalResourceName))
        try:
            api.ExecuteResourceConnectedCommand(reservation_id,
                                                deployment_result.LogicalResourceName,
                                                "remote_refresh_ip",
                                                "remote_connectivity")

        except CloudShellAPIError as exc:
            print "Error refreshing ip for deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                                exc.rawxml)
            logger.error("Error refreshing ip for deployed app {0}. Error: {1}"
                         .format(deployment_result.LogicalResourceName, exc.rawxml))
            raise exc
        except Exception as exc:
            print "Error refreshing ip for deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                                str(exc))
            logger.error("Error refreshing ip for deployed app {0}. Error: {1}"
                         .format(deployment_result.LogicalResourceName, str(exc)))
            raise exc

    @staticmethod
    def execute_installation_if_exist(api, deployment_result, installation_service_data, reservation_id):
        if not installation_service_data:
            return

        installation_service_name = installation_service_data["name"]
        installation_script_name = installation_service_data["scriptCommandName"]
        installation_script_inputs = installation_service_data["scriptInputs"]

        logger.info(
            "Executing installation script '{0}' on installation service '{1}' under deployed app resource '{2}'..."
                .format(installation_script_name, installation_service_name, deployment_result.LogicalResourceName))
        try:

            script_inputs = []
            for installation_script_input in installation_script_inputs:
                script_inputs.append(
                    InputNameValue(installation_script_input["name"], installation_script_input["value"]))

            installation_result = api.InstallApp(reservation_id, deployment_result.LogicalResourceName,
                                                 installation_script_name, script_inputs)
            logger.debug("Installation_result: " + installation_result.Output)
        except CloudShellAPIError as exc:
            print "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                         exc.rawxml)
            logger.error("Error installing deployed app {0}. Error: {1}"
                         .format(deployment_result.LogicalResourceName, exc.rawxml))
            raise exc
        except Exception as exc:
            print "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                         str(exc))
            logger.error(
                "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName, str(exc)))
            raise exc

    @staticmethod
    def power_on_deployed_app(api, app_name, deployment_result, reservation_id):
        try:
            logger.info("Powering on deployed app {0}".format(deployment_result.LogicalResourceName))
            logger.debug("Powering on deployed app {0}. VM UUID: {1}".format(deployment_result.LogicalResourceName,
                                                                             deployment_result.VmUuid))
            api.ExecuteResourceConnectedCommand(reservation_id,
                                                deployment_result.LogicalResourceName,
                                                "PowerOn",
                                                "power")

        except Exception as exc:
            print "Error powering on deployed app {0}. Error: {1}".format(app_name, str(exc))
            logger.error("Error powering on deployed app {0}. Error: {1}".format(app_name, str(exc)))
            raise exc

    @staticmethod
    def deploy_app(api, app_name, deployment_service, reservation_id):
        try:
            logger.info("Executing '{0}' on app '{1}'...".format(deployment_service, app_name))
            return api.DeployAppToCloudProvider(reservation_id, app_name, [InputNameValue("Name", app_name)])
        except CloudShellAPIError as exc:
            print "Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml)
            logger.error("Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml))
            raise exc
        except Exception as exc:
            print "Error deploying app {0}. Error: {1}".format(app_name, str(exc))
            logger.error("Error deploying app {0}. Error: {1}".format(app_name, str(exc)))
            raise exc
