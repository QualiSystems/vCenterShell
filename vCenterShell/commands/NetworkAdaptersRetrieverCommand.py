# -*- coding: utf-8 -*-

import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim

from vCenterShell.commands.BaseCommand import BaseCommand
from vCenterShell.models.VirtualNicModel import VirtualNicModel

from vCenterShell.logger import getLogger
_logger = getLogger(__name__)


#@todo very much trivial implementation. Should be moved & expanded
class ConnectionException(Exception):
    pass


class NetworkAdaptersRetrieverCommand(BaseCommand):
    def __init__(self, pv_service, cs_retriever_service, resource_connection_details_retriever):
        """
        :param pv_service: <pycommon.pyVmomiService obj>
        :param cs_retriever_service:
        :param resource_connection_details_retriever:
        :return:
        """
        self.pvService = pv_service
        self.csRetrieverService = cs_retriever_service
        self.resourceConnectionDetailsRetriever = resource_connection_details_retriever

    def execute(self):
        resource_att = helpers.get_resource_context_details()

        inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_att)
        vcenter_resource_name = inventory_path_data["vCenter_resource_name"]
        vcenter_resource_path = inventory_path_data["vm_folder"]

        connection_details = self.resourceConnectionDetailsRetriever.get_connection_details(vcenter_resource_name)
        message_details = u"'{}:{}' User: '{}'".format(connection_details.host, connection_details.port,
                                                       connection_details.user)
        try:
            si = self.pvService.connect(connection_details.host, connection_details.user, connection_details.password,
                                        connection_details.port)
        except Exception, ex:
            _logger.warn(u"Cannot connect {} Reason: {}".format(message_details, ex))
            raise ConnectionException(message_details)

        _logger.debug(u"Successfully log in {}".format(message_details))

        _logger.debug(u"Retrieving... Path: '{}' Name: '{}'".format(vcenter_resource_path, vcenter_resource_name))
        vm_machine = self.pvService.find_network_by_name(si, vcenter_resource_path, vcenter_resource_name)

        result = [VirtualNicModel(x.deviceInfo.summary,
                                  x.macAddress,
                                  x.connectable.connected,
                                  x.connectable.startConnected)
                    for x in vm_machine.config.hardware.device
                    if isinstance(x, vim.vm.device.VirtualEthernetCard)] if vm_machine else None

        _logger.debug(u"Result: {}".format(result))
        return result



