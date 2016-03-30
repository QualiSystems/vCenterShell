import json
from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.api.cloudshell_api import CloudShellAPISession
from context_based_logger_factory import ContextBasedLoggerFactory


class DeployAppOrchestrationDriver(object):
    NO_DRIVER_ERR = "129"

    def __init__(self):
        self.context_based_logger_factory = ContextBasedLoggerFactory()

    def deploy(self, context):
        """
        Deploys app from template
        :type context: cloudshell.shell.core.context.ResourceCommandContext
        """
        logger = self.context_based_logger_factory.create_logger_for_context(
            logger_name='DeployAppOrchestrationDriver',
            context=context)

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

        self._write_message(app_name, reservation_id, session, 'deployment started')
        deployment_result = self._deploy_app(session, app_name, deployment_service, reservation_id, logger)
        deployed_app_name = deployment_result.LogicalResourceName
        #  self._write_message(deployed_app_name, reservation_id, session, 'Deployment ended successfully')

        # if autoload fails we still want to continue so 'success message' moved inside '_try_exeucte_autoload'
        self._try_execute_autoload(session, reservation_id, deployment_result.LogicalResourceName, logger)

        self._write_message(deployed_app_name, reservation_id, session, 'connecting routes started')
        # if visual connector endpoints contains service with attribute "Virtual Network" execute connect command
        self._connect_routes_on_deployed_app(session, reservation_id, deployment_result.LogicalResourceName, logger)
        self._write_message(deployed_app_name, reservation_id, session, 'connecting routes ended successfully')

        self._write_message(deployed_app_name, reservation_id, session, 'is powering on...')
        self._power_on_deployed_app(session, deployed_app_name, deployment_result, reservation_id, logger)
        self._write_message(deployed_app_name, reservation_id, session, 'powered on successfully')

        self._write_message(deployed_app_name, reservation_id, session,
                            'is waiting for IP address, this may take a while...')
        ip = self._refresh_ip(session, deployment_result, reservation_id, logger)
        self._write_message(deployed_app_name, reservation_id, session,
                            'IP address is {0}'.format(ip) if ip else 'IP address not found')

        # if install service exists on app execute it
        self._execute_installation_if_exist(session, deployment_result, installation_service_data, reservation_id,
                                            logger)

        # Set live status - deployment done
        session.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Online", "Active")

        success_msg = self._format_message(deployed_app_name, 'deployed Successfully')
        logger.info(success_msg)
        return success_msg

    def _write_message(self, app_name, reservation_id, session, message):
        session.WriteMessageToReservationOutput(reservationId=reservation_id,
                                                message=self._format_message(app_name, message))

    def _format_message(self, app_name, message):
        if ' ' in app_name:
            app_name = '"{0}"'.format(app_name)
        return '{0} {1}'.format(app_name, message)

    def _connect_routes_on_deployed_app(self, api, reservation_id, resource_name, logger):
        try:
            reservation = api.GetReservationDetails(reservation_id)
            connectors = [connector for connector in reservation.ReservationDescription.Connectors
                          if connector.State in ['Disconnected', 'PartiallyConnected', 'ConnectionFailed'] and
                          connector.Source == resource_name or connector.Target == resource_name]
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
            raise
        except Exception as exc:
            print "Error executing connect all. Error: {0}".format(str(exc))
            logger.error("Error executing connect all. Error: {0}".format(str(exc)))
            raise

    def _refresh_ip(self, api, deployment_result, reservation_id, logger):
        logger.info(
                "Waiting to get IP for deployed app resource {0}...".format(deployment_result.LogicalResourceName))
        try:
            res = api.ExecuteResourceConnectedCommand(reservation_id,
                                                      deployment_result.LogicalResourceName,
                                                      "remote_refresh_ip",
                                                      "remote_connectivity")
            ip = getattr(res, 'Output', None)
            if not ip:
                return ip
            return ip.replace('command_json_result="', '').replace('"=command_json_result_end', '')

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

    def _execute_installation_if_exist(self, api, deployment_result, installation_service_data, reservation_id, logger):
        if not installation_service_data:
            self._write_message(deployment_result.LogicalResourceName, reservation_id, api,
                                "doesn't have an installation to execute")
            return

        installation_service_name = installation_service_data["name"]
        installation_script_name = installation_service_data["scriptCommandName"]
        installation_script_inputs = installation_service_data["scriptInputs"]

        logger.info(
                "Executing installation script '{0}' on installation service '{1}' under deployed app resource '{2}'..."
                    .format(installation_script_name, installation_service_name, deployment_result.LogicalResourceName))
        self._write_message(deployment_result.LogicalResourceName, reservation_id, api, 'installation started')
        try:

            script_inputs = []
            for installation_script_input in installation_script_inputs:
                script_inputs.append(
                        InputNameValue(installation_script_input["name"], installation_script_input["value"]))

            installation_result = api.InstallApp(reservationId=reservation_id,
                                                 resourceName=deployment_result.LogicalResourceName,
                                                 commandName=installation_script_name,
                                                 commandInputs=script_inputs,
                                                 printOutput=True)

            logger.debug("Installation_result: " + installation_result.Output)
            self._write_message(deployment_result.LogicalResourceName, reservation_id, api,
                                'installation ended successfully')

        except CloudShellAPIError as exc:
            print "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                         exc.rawxml)
            logger.error("Error installing deployed app {0}. Error: {1}"
                              .format(deployment_result.LogicalResourceName, exc.rawxml))
            raise
        except Exception as exc:
            print "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                         str(exc))
            logger.error(
                    "Error installing deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                           str(exc)))
            raise

    def _power_on_deployed_app(self, api, app_name, deployment_result, reservation_id, logger):
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
            raise

    def _deploy_app(self, api, app_name, deployment_service, reservation_id, logger):
        try:
            logger.info("Executing '{0}' on app '{1}'...".format(deployment_service, app_name))
            return api.DeployAppToCloudProvider(reservation_id, app_name, [InputNameValue("Name", app_name)])
        except CloudShellAPIError as exc:
            print "Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml)
            logger.error("Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml))
            raise
        except Exception as exc:
            print "Error deploying app {0}. Error: {1}".format(app_name, str(exc))
            logger.error("Error deploying app {0}. Error: {1}".format(app_name, str(exc)))
            raise

    def _try_execute_autoload(self, session, reservation_id, deployed_app_name, logger):
        """
        :param str reservation_id:
        :param CloudShellAPISession session:
        :param str deployed_app_name:
        :return:
        """
        try:
            logger.info("Executing Autoload command on deployed app {0}".format(deployed_app_name))
            self._write_message(deployed_app_name, reservation_id, session, 'discovery started')

            session.AutoLoad(deployed_app_name)

            self._write_message(deployed_app_name, reservation_id, session, 'discovery ended successfully')
        except CloudShellAPIError as exc:
            if exc.code != DeployAppOrchestrationDriver.NO_DRIVER_ERR:
                print "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name,
                                                                                                exc.rawxml)
                logger.error(
                        "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name,
                                                                                                  exc.rawxml))
                self._write_message(deployed_app_name, reservation_id, session,
                                    'discovery failed: {1}'.format(deployed_app_name, exc.message))
                raise

        except Exception as exc:
            print "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name, str(exc))
            logger.error(
                    "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name,
                                                                                              str(exc)))
            self._write_message(deployed_app_name, reservation_id, session,
                                'discovery failed: {1}'.format(deployed_app_name, exc.message))
