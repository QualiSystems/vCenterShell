from multiprocessing.pool import ThreadPool
import cProfile, pstats, datetime
import cloudshell.api.cloudshell_scripts_helpers as helpers
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

class EnvironmentTeardown:
    def __init__(self):
        self.reservation_id = helpers.get_reservation_context_details().id
        self.logger = qs_logger.get_qs_logger(name="CloudShell Sandbox Teardown",reservation_id=self.reservation_id)

    @profileit("CloudShell_Sandbox_Teardown")
    def execute(self):
        api = helpers.get_api_session()
        reservation_details = api.GetReservationDetails(self.reservation_id)

        self._disconnect_all_routes_in_reservation(api, reservation_details)
        self._power_off_all_vm_resources(api, reservation_details)

        self.logger.info("Teardown for reservation {0} completed".format(self.reservation_id))

    def _disconnect_all_routes_in_reservation(self, api, reservation_details):
        connectors = reservation_details.ReservationDescription.Connectors
        endpoints = []
        for endpoint in connectors:
            endpoints.append(endpoint.Target)
            endpoints.append(endpoint.Source)

        if len(endpoints) == 0:
            self.logger.info("No routes to disconnect for reservation {0}".format(self.reservation_id))
            return

        self.logger.info("Executing disconnect routes for reservation {0}".format(self.reservation_id))

        try:
            api.DisconnectRoutesInReservation(self.reservation_id, endpoints)
        except Exception as exc:
            self.logger.error("Error disconnecting all routes in reservation {0}. Error: {1}"
                         .format(self.reservation_id, str(exc)))

    def _power_off_all_vm_resources(self, api, reservation_details):
        resources = reservation_details.ReservationDescription.Resources

        pool = ThreadPool()

        for resource in resources:
            resource_details = api.GetResourceDetails(resource.Name)
            if resource_details.VmDetails:
                pool.apply_async(self._power_off_or_delete_deployed_app, (api, resource_details))

        pool.close()
        pool.join()

    def _power_off_or_delete_deployed_app(self, api, resource_info):
        """
        :param api:
        :param ResourceInfo resource_info:
        :return:
        """
        try:
            resource_name = resource_info.Name

            delete = "true"
            auto_delete_param = get_vm_custom_param(resource_info.VmDetails.VmCustomParams, "auto_delete")
            if auto_delete_param:
                delete = auto_delete_param.Value

            if delete.lower() == "true":
                self.logger.info("Executing 'Delete' on deployed app {0} in reservation {1}"
                            .format(resource_name, self.reservation_id))
                api.ExecuteResourceConnectedCommand(self.reservation_id, resource_name, "remote_destroy_vm",
                                                    "remote_app_management")
            else:
                power_off = "true"
                auto_power_off_param = get_vm_custom_param(resource_info.VmDetails.VmCustomParams, "auto_power_off")
                if auto_power_off_param:
                    power_off = auto_power_off_param.Value

                if power_off.lower() == "true":
                    self.logger.info("Executing 'Power Off' on deployed app {0} in reservation {1}"
                                .format(resource_name, self.reservation_id))
                    api.ExecuteResourceConnectedCommand(self.reservation_id, resource_name, "PowerOff", "power")
                else:
                    self.logger.info("Auto Power Off is disabled for deployed app {0} in reservation {1}"
                                .format(resource_name, self.reservation_id))
            return True
        except Exception as exc:
            self.logger.error("Error powering off deployed app {0} in reservation {1}. Error: {2}"
                         .format(resource_name, self.reservation_id, str(exc)))
            return False
