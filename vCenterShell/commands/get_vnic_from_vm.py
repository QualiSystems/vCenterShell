# -*- coding: utf-8 -*-

import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim
from models.VirtualNicModel import VirtualNicModel
from common.logger import getLogger

_logger = getLogger("vCenterShell")

#@todo very much trivial implementation. Should be moved & expanded
class ConnectionException(Exception):
    pass


class NetworkAdaptersRetrieverCommand(object):
    def __init__(self, pv_service, cs_retriever_service, resource_connection_details_retriever):
        """
        :param pv_service: <common.pyVmomiService obj>
        :param cs_retriever_service: <common.CloudshellDataRetrieverService obj>
        :param resource_connection_details_retriever: <common.ResourceConnectionDetailsRetriever obj>
        :return:
        """
        self.pvService = pv_service
        self.csRetrieverService = cs_retriever_service
        self.resourceConnectionDetailsRetriever = resource_connection_details_retriever

    def execute(self):
        resource_att = helpers.get_resource_context_details()

        inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_att)
        resource_name = inventory_path_data["vCenter_resource_name"]
        resource_path = inventory_path_data["vm_folder"]

        connection_details = self.resourceConnectionDetailsRetriever.get_connection_details(resource_name)
        message_details = u"'{}:{}' User: '{}'".format(connection_details.host,
                                                       connection_details.port,
                                                       connection_details.user)
        try:
            si = self.pvService.connect(connection_details.host,
                                        connection_details.user,
                                        connection_details.password,
                                        connection_details.port)
        except Exception, ex:
            _logger.warn(u"Cannot connect {} Reason: {}".format(message_details, ex))
            raise ConnectionException(message_details)

        _logger.debug(u"Successfully log in {}".format(message_details))

        return NetworkAdaptersRetrieverCommand.retrieve(self.pvService, si, resource_path, resource_name)


    @staticmethod
    def retrieve(pvService, si, path, network_name):
        """
        Retrieve Network by Name
        :param pv_service: <common.pyVmomiService obj>
        :param si: <service instance>
        :param path: <str>
        :param network_name: <str>
        :return: <list of 'VirtualNicModel'>
        """
        _logger.debug(u"Retrieving Network... Path: '{}' Name: '{}'".format(path, network_name))
        vm_machine = pvService.find_network_by_name(si, path, network_name)

        result = [VirtualNicModel(x.deviceInfo.summary,
                                  x.macAddress,
                                  x.connectable.connected,
                                  x.connectable.startConnected)
                    for x in vm_machine.config.hardware.device
                    if isinstance(x, vim.vm.device.VirtualEthernetCard)] if vm_machine else None
        _logger.debug(u"Retrieving Network Result: {}".format(result))

        return result
