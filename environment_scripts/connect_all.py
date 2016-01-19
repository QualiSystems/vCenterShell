import re

import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import InputNameValue, AttributeNameValue
from common.utilites.command_result import get_result_from_command_output

from common.logger.service import getLogger
_logger = getLogger('EnvironmentConnector')

VIRTUAL_NETWORK_ATTRIBUTE = 'Virtual Network'
ACCESS_MODE_ATTRIBUTE = 'Access Mode'


class EnvironmentConnector(object):
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

            access_mode = self._get_attribute(vlan_service.Attributes, ACCESS_MODE_ATTRIBUTE)
            virtual_network = self._get_attribute(vlan_service.Attributes, VIRTUAL_NETWORK_ATTRIBUTE)

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
    def _get_attribute(attributes, attribute_name):
        attribute = next(item for item in attributes if item.Name == attribute_name)
        if not attribute:
            raise ValueError('Attribute {0} is missing'.format(attribute_name))
        return attribute.Value

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

        command_result = session.ExecuteCommand(reservation_id, connected_resource, 'Resource', 'Connect',
                                                [InputNameValue('VLAN_ID', virtual_network),
                                                 InputNameValue('VLAN_SPEC_TYPE', access_mode)], True)

        result = get_result_from_command_output(command_result.Output)

        if not result:
            _logger.debug('Connect command did not return any result')
            return

        mac_address = result.replace('[\'', '').replace('\']', '')
        _logger.debug('Setting Target Interface to: ' + mac_address)

        session.SetConnectorAttributes(reservation_id,
                                       connected_resource,
                                       vlan_service_name,
                                       [AttributeNameValue('Target Interface', mac_address)])

    @staticmethod
    def _get_connected_resources(connectors, vlan_service):
        connected_resources = [connector.Target for connector in connectors if
                               connector.Source == vlan_service.ServiceName] + \
                              [connector.Source for connector in connectors if
                               connector.Target == vlan_service.ServiceName]
        return connected_resources
