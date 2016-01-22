# -*- coding: utf-8 -*-

from models.named_entry import NamedEntry

from common.logger import getLogger

### NOT USED:
# _logger = getLogger("vCenterCommon")
#
#
# class VirtualSwitch(NamedEntry):
#     def __init__(self, switch_name, vlan_type="", number_of_ports=32):
#         """
#         :param switch_name: <str> name of switch
#         :param number_of_ports: <int> Number of ports
#         :param vlan_type: <str> ?
#         """
#         super(VirtualSwitch, self).__init__(switch_name)
#
#         self.number_of_ports = number_of_ports
#         self.vlan_type = vlan_type
#
#         self.network = None
#
#     def connected(self):
#         return bool(self.network)
#
#     def __str__(self):
#         return "VirtualSwitch '{}' type: [{}]. Status: '{}' Network: '{}'".format(
#             self.name, self.vlan_type, "CONNECTED" if self.connected() else "DISCONNECTED", self.network)
#
#     def attach(self, network):
#         self.network = network
#         _logger.debug("{} just attached".format(self))
#         pass
#
#     def destroy(self):
#         if self.connected():
#             self.network = None
#             pass