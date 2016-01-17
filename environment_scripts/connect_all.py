import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import InputNameValue
from common.utilites.common_utils import first_or_default

from common.model_factory import ResourceModelParser


class EnvironmentConnector(object):

    def connect_all(self):
        """
        Connects all the VLAN Auto services to all the Deployed Apps in the same Environment
        :return:
        """

        resource_model_parser = ResourceModelParser()
        session = helpers.get_api_session()
        reservation_id = helpers.get_reservation_context_details().id

        # GetReservationDetails is performance heavy operation
        reservation_details = session.GetReservationDetails(reservation_id)
        vlan_services = self._get_vlan_auto_services(reservation_details)

        connectors = self._get_connectors(reservation_details)

        if not vlan_services or not connectors:
            return

        for vlan_service in vlan_services:

            access_mode = next(item for item in vlan_service.Attributes if item.Name == 'Access Mode')
            virtual_network = next(item for item in vlan_service.Attributes if item.Name == 'Virtual Network')

            # Get Deployed App connected to VLAN Auto service
            connected_resources = self._get_connected_resources(connectors, vlan_service)

            if not connected_resources:
                continue

            for connected_resource in connected_resources:
                self._execute_connect_command_on_connected_resource(access_mode, connected_resource, reservation_id,
                                                                    session, virtual_network)

    @staticmethod
    def _get_connectors(reservation_details):
        connectors = [connector for connector in reservation_details.ReservationDescription.Connectors]
        return connectors

    @staticmethod
    def _get_vlan_auto_services(reservation_details):
        vlan_services = [service for service in reservation_details.ReservationDescription.Services
                         if service.ServiceName == 'VLAN Auto']
        return vlan_services

    @staticmethod
    def _execute_connect_command_on_connected_resource(access_mode, connected_resource, reservation_id, session,
                                                       virtual_network):
        session.ExecuteCommand(reservation_id, connected_resource, 'Resource', 'Connect',
                               [InputNameValue('COMMAND', "connect"),
                                InputNameValue('VLAN_ID', virtual_network),
                                InputNameValue('VLAN_SPEC_TYPE', access_mode)],
                               True)

    @staticmethod
    def _get_connected_resources(connectors, vlan_service):
        connected_resources = [connector.Target for connector in connectors if
                               connector.Source == vlan_service.ServiceName] + \
                              [connector.Source for connector in connectors if
                               connector.Target == vlan_service.ServiceName]
        return connected_resources
