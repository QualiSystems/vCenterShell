import qualipy.scripts.cloudshell_scripts_helpers as helpers
from qualipy.api.cloudshell_api import InputNameValue

session = helpers.get_api_session()
reservation_id = helpers.get_reservation_context_details().id
connectors = session.GetReservationDetails(reservation_id).ReservationDescription.Connectors
attributes = helpers.get_resource_context_details().attributes
vlan = attributes['VLAN Id']
access_mode = attributes['Access Mode']
resource_name = helpers.get_resource_context_details().name

connectedResources = [connector.Target for connector in connectors if connector.Source == resource_name] + \
             [connector.Source for connector in connectors if connector.Target == resource_name]

if not connectedResources:
    raise Exception('There is no visual connectors connected to this VLAN')

for connectedResource in connectedResources:
    session.ExecuteCommand(reservation_id, connectedResource, 'Resource', 'Connect',
                           [InputNameValue('COMMAND', "connect"),
                            InputNameValue('VLAN_ID', vlan),
                            InputNameValue('VLAN_SPEC_TYPE', access_mode)],
                           True)
