import json
from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.api.cloudshell_api import CloudShellAPISession



class DeployAppOrchestrationDriver(object):


    def initialize(self, context):
        """
        Deploys app from template
        :type context: cloudshell.shell.core.driver_context.InitCommandContext
        """
        self.logger = get_qs_logger(handler_name=context.resource.name)

    def deploy(self, context):
        """
        Deploys app from template
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        """
        reservation_id = context.reservation.reservation_id
        resource_details = context.resource
        app_name = resource_details.name
        app_data = json.loads(resource_details.app_context.app_request_json)
        deployment_service = app_data["deploymentService"]["name"]
        installation_service_data = app_data["installationService"]

        # Start api session
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                             token_id=context.connectivity.admin_auth_token,
                                             domain=context.reservation.domain)
        # execute deploy app
        deployment_result = self._deploy_app(session, app_name, deployment_service, reservation_id)

        # if visual connector endpoints contains service with attribute "Virtual Network" execute connect command
        self._connect_routes_on_deployed_app(session, reservation_id, deployment_result.LogicalResourceName)

        # "Power On"
        self._power_on_deployed_app(session, app_name, deployment_result, reservation_id)

        # refresh ip
        self._refresh_ip(session, deployment_result, reservation_id)

        # if install service exists on app execute it
        self._execute_installation_if_exist(session, deployment_result, installation_service_data, reservation_id)

        # Set live status - deployment done
        session.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Online", "Active")

        self.logger.info("Deployed {0} Successfully".format(deployment_result.LogicalResourceName))
        return "Deployed {0} Successfully".format(deployment_result.LogicalResourceName)

    def _connect_routes_on_deployed_app(self, api, reservation_id, resource_name):
        try:
            reservation = api.GetReservationDetails(reservation_id)
            connectors = [connector for connector in reservation.ReservationDescription.Connectors
                          if connector.Source == resource_name or connector.Target == resource_name]
            endpoints = []
            for endpoint in connectors:
                endpoints.append(endpoint.Target)
                endpoints.append(endpoint.Source)

            if len(endpoints) == 0:
                self.logger.info("No routes to connect for app {0}".format(resource_name))
                return

            self.logger.info("Executing connect for app {0}".format(resource_name))
            api.ConnectRoutesInReservation(reservation_id, endpoints, 'bi')

        except CloudShellAPIError as exc:
            print "Error executing connect all. Error: {0}".format(exc.rawxml)
            self.logger.error("Error executing connect all. Error: {0}".format(exc.rawxml))
            raise exc
        except Exception as exc:
            print "Error executing connect all. Error: {0}".format(str(exc))
            self.logger.error("Error executing connect all. Error: {0}".format(str(exc)))
            raise exc

    def _refresh_ip(self, api, deployment_result, reservation_id):
        self.logger.info("Waiting to get IP for deployed app resource {0}...".format(deployment_result.LogicalResourceName))
        try:
            api.ExecuteResourceConnectedCommand(reservation_id,
                                                deployment_result.LogicalResourceName,
                                                "remote_refresh_ip",
                                                "remote_connectivity")

        except CloudShellAPIError as exc:
            print "Error refreshing ip for deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                                exc.rawxml)
            self.logger.error("Error refreshing ip for deployed app {0}. Error: {1}"
                         .format(deployment_result.LogicalResourceName, exc.rawxml))
            raise exc
        except Exception as exc:
            print "Error refreshing ip for deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                                str(exc))
            self.logger.error("Error refreshing ip for deployed app {0}. Error: {1}"
                         .format(deployment_result.LogicalResourceName, str(exc)))
            raise exc

    def _execute_installation_if_exist(self, api, deployment_result, installation_service_data, reservation_id):
        if not installation_service_data:
            return

        installation_service_name = installation_service_data["name"]
        installation_script_name = installation_service_data["scriptCommandName"]
        installation_script_inputs = installation_service_data["scriptInputs"]

        self.logger.info(
            "Executing installation script '{0}' on installation service '{1}' under deployed app resource '{2}'..."
                .format(installation_script_name, installation_service_name, deployment_result.LogicalResourceName))
        try:

            script_inputs = []
            for installation_script_input in installation_script_inputs:
                script_inputs.append(
                    InputNameValue(installation_script_input["name"], installation_script_input["value"]))

            installation_result = api.InstallApp(reservation_id, deployment_result.LogicalResourceName,
                                                 installation_script_name, script_inputs)
            self.logger.debug("Installation_result: " + installation_result.Output)
        except CloudShellAPIError as exc:
            print "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                         exc.rawxml)
            self.logger.error("Error installing deployed app {0}. Error: {1}"
                         .format(deployment_result.LogicalResourceName, exc.rawxml))
            raise exc
        except Exception as exc:
            print "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                         str(exc))
            self.logger.error(
                "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName, str(exc)))
            raise exc

    def _power_on_deployed_app(self, api, app_name, deployment_result, reservation_id):
        try:
            self.logger.info("Powering on deployed app {0}".format(deployment_result.LogicalResourceName))
            self.logger.debug("Powering on deployed app {0}. VM UUID: {1}".format(deployment_result.LogicalResourceName,
                                                                             deployment_result.VmUuid))
            api.ExecuteResourceConnectedCommand(reservation_id,
                                                deployment_result.LogicalResourceName,
                                                "PowerOn",
                                                "power")

        except Exception as exc:
            print "Error powering on deployed app {0}. Error: {1}".format(app_name, str(exc))
            self.logger.error("Error powering on deployed app {0}. Error: {1}".format(app_name, str(exc)))
            raise exc

    def _deploy_app(self, api, app_name, deployment_service, reservation_id):
        try:
            self.logger.info("Executing '{0}' on app '{1}'...".format(deployment_service, app_name))
            return api.DeployAppToCloudProvider(reservation_id, app_name, [InputNameValue("Name", app_name)])
        except CloudShellAPIError as exc:
            print "Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml)
            self.logger.error("Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml))
            raise exc
        except Exception as exc:
            print "Error deploying app {0}. Error: {1}".format(app_name, str(exc))
            self.logger.error("Error deploying app {0}. Error: {1}".format(app_name, str(exc)))
            raise exc
