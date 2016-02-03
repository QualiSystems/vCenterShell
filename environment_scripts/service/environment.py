import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import InputNameValue, AttributeNameValue
from common.logger.service import getLogger
from common.utilites.command_result import get_result_from_command_output
from common.cloudshell.resource_helper import get_attribute

_logger = getLogger('EnvironmentConnector')

VIRTUAL_NETWORK_ATTRIBUTE = 'Virtual Network'
ACCESS_MODE_ATTRIBUTE = 'Access Mode'


class EnvironmentService(object):
    @staticmethod
    def connect_bulk():
        """

        """
        raise Exception('Not implemented')

    def connect_all(self):
        """
        Connects all the VLAN Auto services to all the Deployed Apps in the same Environment
        :return:
        """
        session = helpers.get_api_session()
        reservation_id = helpers.get_reservation_context_details().id

        # GetReservationDetails is performance heavy operation
        reservation_details = session.GetReservationDetails(reservation_id)
        vlan_services = self._get_vlan_auto_services(reservation_details)

        connectors = self._get_connectors(reservation_details)

        if not vlan_services or not connectors:
            return

        for vlan_service in vlan_services:

            _logger.debug('Connecting \'{0}\' '.format(vlan_service.ServiceName))

            access_mode = get_attribute(vlan_service.Attributes, ACCESS_MODE_ATTRIBUTE)
            virtual_network = get_attribute(vlan_service.Attributes, VIRTUAL_NETWORK_ATTRIBUTE)

            # Get Deployed App connected to VLAN Auto service
            connected_resources = self._get_connected_resources(connectors, vlan_service)

            if not connected_resources:
                continue

            if not virtual_network or virtual_network == '':

                _logger.debug('Executing Auto Resolve Vlan on \'{0}\''.format(vlan_service.ServiceName))

                command_result = session.ExecuteCommand(reservation_id, vlan_service.ServiceName, 'Service',
                                                        'Auto Resolve Vlan', [], True)

                virtual_network = get_result_from_command_output(command_result.Output)

                _logger.debug('Auto Resolve Vlan returned Virtual Network \'{0}\''.format(virtual_network))

                if not virtual_network or virtual_network == '':
                    raise ValueError('Auto Resolve Vlan command did not return Virtual Network')

            for connected_resource in connected_resources:
                self._execute_connect_command_on_connected_resource(access_mode, connected_resource, reservation_id,
                                                                    session, virtual_network, vlan_service.ServiceName)

    @staticmethod
    def _get_connectors(reservation_details):
        connectors = [connector for connector in reservation_details.ReservationDescription.Connectors]
        return connectors

    @staticmethod
    def _get_vlan_auto_services(reservation_details):
        vlan_services = [service for service in reservation_details.ReservationDescription.Services
                         if VIRTUAL_NETWORK_ATTRIBUTE in [attr.Name for attr in service.Attributes]]
        return vlan_services

    @staticmethod
    def _execute_connect_command_on_connected_resource(access_mode, connected_resource, reservation_id, session,
                                                       virtual_network, vlan_service_name):

        _logger.debug('Executing Connect command on: ' + connected_resource)

        command_result = session.ExecuteCommand(reservation_id, connected_resource, 'Resource', 'connect_bulk',
                                                [InputNameValue('vlan_id', virtual_network),
                                                 InputNameValue('vlan_spec_type', access_mode)], True)

        connect_results = get_result_from_command_output(command_result.Output)

        if not connect_results:
            _logger.debug('Connect command did not return any results')
            return

        for connect_result in connect_results:
            mac_address = connect_result['mac_address']
            _logger.debug('Setting Target Interface to: ' + mac_address)
            session.SetConnectorAttributes(reservation_id,
                                           connected_resource,
                                           vlan_service_name,
                                           [AttributeNameValue('Target Interface', mac_address)])
            break

    @staticmethod
    def _get_connected_resources(connectors, vlan_service):
        connected_resources = [connector.Target for connector in connectors if
                               connector.Source == vlan_service.ServiceName] + \
                              [connector.Source for connector in connectors if
                               connector.Target == vlan_service.ServiceName]
        return connected_resources
