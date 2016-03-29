from unittest import TestCase

import jsonpickle

from cloudshell.cp.vcenter.models.DeployDataHolder import DeployDataHolder


class TestDeployDataHolder(TestCase):
    def test_deploy_data_holder(self):
        # Arrange
        json = '''
            {
              "driverRequest": {
                "actions": [
                  {
                      "actionId": "vlan1%<=>%resourceA",
                      "type": "setVlan",
                      "actionTarget": {
                        "fullName": "Chassis1/Blade1/port1",
                        "fullAddress" : "1/2/3"
                      },
                      "connectionId" : "vlan1%<=>%resourceA",
                      "connectionParams" : {
                        "connectionParams" : "setVlanParameter",
                        "vlanIds" : ["100-200", "300"],
                        "mode" : "Trunk"
                      },
                      "connectorAttributes" : [
                            {
                                "type": "connectorAttribute",
                                "attributeName" : "QNQ",
                                "attributeValue" : "Enabled"
                            }
                      ]

                  }
                ]
              }
            }   '''

        dictionary = jsonpickle.decode(json)

        # Act
        holder = DeployDataHolder(dictionary)

        # Assert
        self.assertEqual(holder.driverRequest.actions[0].actionId, 'vlan1%<=>%resourceA')
        self.assertEqual(holder.driverRequest.actions[0].type, 'setVlan')
        self.assertEqual(holder.driverRequest.actions[0].actionTarget.fullName, 'Chassis1/Blade1/port1')
        self.assertEqual(holder.driverRequest.actions[0].actionTarget.fullAddress, '1/2/3')
        self.assertEqual(holder.driverRequest.actions[0].connectionId, 'vlan1%<=>%resourceA')
        self.assertEqual(holder.driverRequest.actions[0].connectionParams.connectionParams, 'setVlanParameter')
        self.assertEqual(holder.driverRequest.actions[0].connectionParams.vlanIds[0], '100-200')
        self.assertEqual(holder.driverRequest.actions[0].connectionParams.vlanIds[1], '300')
        self.assertEqual(holder.driverRequest.actions[0].connectionParams.mode, 'Trunk')
        self.assertEqual(holder.driverRequest.actions[0].connectorAttributes[0].type, 'connectorAttribute')
        self.assertEqual(holder.driverRequest.actions[0].connectorAttributes[0].attributeName, 'QNQ')
        self.assertEqual(holder.driverRequest.actions[0].connectorAttributes[0].attributeValue, 'Enabled')

    def test_deploy_data_holder_with_inner_list(self):
        # Arrange
        json = '''
            {
              "driverRequest": {
                "actions": [
                      [
                        "setVlanParameter",
                        ["100-200", "300"]
                      ]
                ]
              }
            }   '''

        dictionary = jsonpickle.decode(json)

        # Act
        holder = DeployDataHolder(dictionary)

        # Assert
        self.assertEqual(holder.driverRequest.actions[0][1][0], '100-200')
        self.assertEqual(holder.driverRequest.actions[0][1][1], '300')

