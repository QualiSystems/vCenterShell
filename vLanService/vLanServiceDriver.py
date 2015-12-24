import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import InputNameValue

session = helpers.get_api_session()
reservation_id = helpers.get_reservation_context_details().id
connectors = session.GetReservationDetails(reservation_id).ReservationDescription.Connectors
attributes = helpers.get_resource_context_details().attributes
vlan = attributes['VLAN Id']
access_mode = attributes['Access Mode']
atLeastOneConnected = False
for connector in connectors:
    if connector.Source == helpers.get_resource_context_details().name:
        session.ExecuteCommand(reservation_id, connector.Target, 'Resource', 'Connect',
                               [InputNameValue('COMMAND', "connect"),
                                InputNameValue('VLAN_ID', vlan),
                                InputNameValue('VLAN_SPEC_TYPE', access_mode)],
                               True)
        atLeastOneConnected = True

if not atLeastOneConnected:
    raise Exception('There is no visual connectors connected to this VLAN')