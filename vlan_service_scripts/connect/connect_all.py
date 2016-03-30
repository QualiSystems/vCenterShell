from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helpers
from cloudshell.core.logger import qs_logger


class ConnectAll:
    def __init__(self):
        self.reservation_id = helpers.get_reservation_context_details().id
        self.logger = qs_logger.get_qs_logger(log_file_prefix='Connect_All',
                                              log_group=self.reservation_id,
                                              log_category="Connect All")

    def execute(self):
        api = helpers.get_api_session()

        reservation = api.GetReservationDetails(self.reservation_id)
        resource_name = helpers.get_resource_context_details_dict()['name']

        all_resources = [resource.Name for resource in reservation.ReservationDescription.Resources]
        all_resources.append(resource_name)

        connectors = [connector
                      for connector in reservation.ReservationDescription.Connectors
                      if connector.State in ['Disconnected', 'PartiallyConnected', 'ConnectionFailed'] and
                      (connector.Source == resource_name or connector.Target == resource_name) and
                      connector.Source in all_resources and connector.Target in all_resources]

        endpoints = []
        for endpoint in connectors:
            endpoints.append(endpoint.Target)
            endpoints.append(endpoint.Source)

        self.logger.info("Executing connect for app {0}".format(resource_name))
        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='[{0}] connecting all routes'.format(resource_name))
        if endpoints:
            api.ConnectRoutesInReservation(self.reservation_id, endpoints, 'bi')
        api.WriteMessageToReservationOutput(reservationId=self.reservation_id,
                                            message='[{0}] connecting all finished successfully'.format(resource_name))
