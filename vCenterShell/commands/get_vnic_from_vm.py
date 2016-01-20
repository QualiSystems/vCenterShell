# -*- coding: utf-8 -*-

from pyVmomi import vim
from models.VirtualNicModel import VirtualNicModel
from common.logger import getLogger

_logger = getLogger("vCenterShell")


# @todo very much trivial implementation. Should be moved & expanded
class ConnectionException(Exception):
    pass


class NetworkAdaptersRetrieverCommand(object):
    def __init__(self, pv_service):
        """
        :param pv_service: <common.pv_service obj>
        :return:
        """
        self.pv_service = pv_service

    def retrieve(self, si, path, network_name):
        """
        Retrieve Network by Name
        :param si: <service instance>
        :param path: <str> the path to find the vm network
        :param network_name: <str>
        :return: <list of 'VirtualNicModel'>
        """
        _logger.debug("Retrieving Network... Path: '{0}' Name: '{1}'".format(path, network_name))
        vm_machine = self.pv_service.find_network_by_name(si, path, network_name)

        result = [VirtualNicModel(x.deviceInfo.summary,
                                  x.macAddress,
                                  x.connectable.connected,
                                  x.connectable.startConnected)
                  for x in vm_machine.config.hardware.device
                  if isinstance(x, vim.vm.device.VirtualEthernetCard)] if vm_machine else None
        _logger.debug("Retrieving Network Result: {0}".format(result))

        return result
