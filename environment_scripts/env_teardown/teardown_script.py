# coding=utf-8
from multiprocessing.pool import ThreadPool
from threading import Lock

from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helpers
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.core.logger import qs_logger
from environment_scripts.profiler.env_profiler import profileit
from environment_scripts.helpers.vm_details_helper import get_vm_custom_param


class EnvironmentTeardown:
    def __init__(self):
        self.reservation_id = helpers.get_reservation_context_details().id
        self.logger = qs_logger.get_qs_logger(log_file_prefix="CloudShell Sandbox Teardown",
                                              log_group=self.reservation_id,
                                              log_category='Teardown')

    @profileit(scriptName="Teardown")
    def execute(self):
        api = helpers.get_api_session()
        reservation_details = api.GetReservationDetails(self.reservation_id)

        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='Beginning reservation teardown')

        self._disconnect_all_routes_in_reservation(api, reservation_details)

        self._power_off_and_delete_all_vm_resources(api, reservation_details)

        self.logger.info("Teardown for reservation {0} completed".format(self.reservation_id))
        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='Reservation teardown finished successfully')

    def _disconnect_all_routes_in_reservation(self, api, reservation_details):
        connectors = reservation_details.ReservationDescription.Connectors
        endpoints = []
        for endpoint in connectors:
            if endpoint.Target and endpoint.Source:
                endpoints.append(endpoint.Target)
                endpoints.append(endpoint.Source)

        if not endpoints:
            self.logger.info("No routes to disconnect for reservation {0}".format(self.reservation_id))
            api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                message="Nothing to disconnecting")
            return

        try:
            self.logger.info("Executing disconnect routes for reservation {0}".format(self.reservation_id))
            api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                message="Disconnecting all apps...")
            api.DisconnectRoutesInReservation(self.reservation_id, endpoints)

        except CloudShellAPIError as cerr:
            if cerr.code != "123":  # ConnectionNotFound error code
                self.logger.error("Error disconnecting all routes in reservation {0}. Error: {1}"
                                  .format(self.reservation_id, str(cerr)))
                api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                    message="Error disconnecting apps. Error: {0}".format(cerr.message))

        except Exception as exc:
            self.logger.error("Error disconnecting all routes in reservation {0}. Error: {1}"
                              .format(self.reservation_id, str(exc)))
            api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                message="Error disconnecting apps. Error: {0}".format(exc.message))

    def _power_off_and_delete_all_vm_resources(self, api, reservation_details):
        resources = reservation_details.ReservationDescription.Resources

        pool = ThreadPool()
        async_results = []
        lock = Lock()
        message_status = {
            "power_off": False,
            "delete": False
        }

        for resource in resources:
            resource_details = api.GetResourceDetails(resource.Name)
            if resource_details.VmDetails:
                result_obj = pool.apply_async(self._power_off_or_delete_deployed_app,
                                              (api, resource_details, lock, message_status))
                async_results.append(result_obj)

        pool.close()
        pool.join()

        resource_to_delete = []
        for async_result in async_results:
            result = async_result.get()
            if result is not None:
                resource_to_delete.append(result)

        # delete resource - bulk
        if resource_to_delete:
            api.DeleteResources(resource_to_delete)

    def _power_off_or_delete_deployed_app(self, api, resource_info, lock, message_status):
        """
        :param CloudShellAPISession api:
        :param Lock lock:
        :param (dict of str: Boolean) message_status:
        :param ResourceInfo resource_info:
        :return:
        """
        resource_name = resource_info.Name
        try:
            delete = "true"
            auto_delete_param = get_vm_custom_param(resource_info.VmDetails.VmCustomParams, "auto_delete")
            if auto_delete_param:
                delete = auto_delete_param.Value

            if delete.lower() == "true":
                self.logger.info("Executing 'Delete' on deployed app {0} in reservation {1}"
                                 .format(resource_name, self.reservation_id))

                if not message_status['delete']:
                    with lock:
                        if not message_status['delete']:
                            message_status['delete'] = True
                            if not message_status['power_off']:
                                message_status['power_off'] = True
                                api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                                    message='Apps are being powered off and deleted...')
                            else:
                                api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                                    message='Apps are being deleted...')

                api.ExecuteResourceConnectedCommand(self.reservation_id,
                                                    resource_name,
                                                    "destroy_vm_only",
                                                    "remote_app_management")
                return resource_name
            else:
                power_off = "true"
                auto_power_off_param = get_vm_custom_param(resource_info.VmDetails.VmCustomParams, "auto_power_off")
                if auto_power_off_param:
                    power_off = auto_power_off_param.Value

                if power_off.lower() == "true":
                    self.logger.info("Executing 'Power Off' on deployed app {0} in reservation {1}"
                                     .format(resource_name, self.reservation_id))

                    if not message_status['power_off']:
                        with lock:
                            if not message_status['power_off']:
                                message_status['power_off'] = True
                                api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                                                    message='Apps are powering off...')

                    api.ExecuteResourceConnectedCommand(self.reservation_id, resource_name, "PowerOff", "power")
                else:
                    self.logger.info("Auto Power Off is disabled for deployed app {0} in reservation {1}"
                                     .format(resource_name, self.reservation_id))
            return None
        except Exception as exc:
            self.logger.error("Error deleting or powering off deployed app {0} in reservation {1}. Error: {2}"
                              .format(resource_name, self.reservation_id, str(exc)))
            return None
