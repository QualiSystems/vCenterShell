from unittest import TestCase
from common.cloudshell.bulk_request_builder import BulkRequestBuilder
from common.cloudshell.connectivity_schema import Action


class TestBulkRequestBuilder(TestCase):
    def test_bulk_request_builder(self):
        bulk_request_builder = BulkRequestBuilder()
        action = Action()
        action.actionId = 'vlan1%<=>%resourceA'
        action.type = 'setVlan'
        action.actionTarget = {
            "fullName": "Chassis1/Blade1/port1",
            "fullAddress" : "1/2/3"
          }
        action.connectionId = 'vlan1%<=>%resourceA'
        action.connectionParams = {
            "type": "setVlanParameter",
            "vlanIds": ["100-200", "300"],
            "mode": "Trunk"
          }
        action.connectorAttributes = [
                {
                    "type": "connectorAttribute",
                    "attributeName": "QNQ",
                    "attributeValue": "Enabled"
                }
          ]
        bulk_request_builder.append_action(action)

        # Act
        request = bulk_request_builder.get_request()

        # Assert
        self.assertEqual(request, '{"actions": [{"connectorAttributes": [{"type": "connectorAttribute", "attributeName": "QNQ", "attributeValue": "Enabled"}], "actionTarget": {"fullAddress": "1/2/3", "fullName": "Chassis1/Blade1/port1"}, "connectionParams": {"vlanIds": ["100-200", "300"], "type": "setVlanParameter", "mode": "Trunk"}, "connectionId": "vlan1%<=>%resourceA", "actionId": "vlan1%<=>%resourceA", "type": "setVlan", "conenctionId": ""}]}')
