from multiprocessing.pool import ThreadPool

import cloudshell.api.cloudshell_scripts_helpers as helpers
from cloudshell.api.cloudshell_api import *

from common.logger import getLogger

logger = getLogger("CloudShell Sandbox Teardown")


class EnvironmentTeardown:
    def __init__(self):
        self.reservation_id = helpers.get_reservation_context_details().id

    def execute(self):
        api = helpers.get_api_session()
        reservation_details = api.GetReservationDetails(self.reservation_id)

        self._disconnect_all_routes_in_reservation(api, reservation_details)
        self._power_off_all_vm_resources(api, reservation_details)

        logger.info("Teardown for reservation {0} completed".format(self.reservation_id))

    def _disconnect_all_routes_in_reservation(self, api, reservation_details):
        connectors = reservation_details.ReservationDescription.Connectors
        endpoints = []
        for endpoint in connectors:
            endpoints.append(endpoint.Target)
            endpoints.append(endpoint.Source)

        if len(endpoints) == 0:
            logger.info("No routes to disconnect for reservation {0}".format(self.reservation_id))
            return

        logger.info("Executing disconnect routes for reservation {0}".format(self.reservation_id))

        try:
            api.DisconnectRoutesInReservation(self.reservation_id, endpoints)
        except Exception as exc:
            logger.error("Error disconnecting all routes in reservation {0}. Error: {1}"
                         .format(self.reservation_id, str(exc)))

    def _power_off_all_vm_resources(self, api, reservation_details):
        resources = reservation_details.ReservationDescription.Resources

        pool = ThreadPool()

        for resource in resources:
            resource_details = api.GetResourceDetails(resource.Name)
            if resource_details.VmDetails:
                pool.apply_async(self._power_off_resource, (api, resource_details.Name))

        pool.close()
        pool.join()

    def _power_off_resource(self, api, resource_name):
        try:
            logger.info("Executing 'Power Off' on deployed app {0} in reservation {1}"
                        .format(resource_name, self.reservation_id))
            api.ExecuteResourceConnectedCommand(self.reservation_id, resource_name, "PowerOff", "power")
            return True
        except Exception as exc:
            logger.error("Error powering off deployed app {0} in reservation {1}. Error: {2}"
                         .format(resource_name, self.reservation_id, str(exc)))
            return False
