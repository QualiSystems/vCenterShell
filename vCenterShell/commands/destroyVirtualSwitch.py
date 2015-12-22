# -*- coding: utf-8 -*-

import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim

from vCenterShell.commands.BaseCommand import BaseCommand
from vCenterShell.models.VirtualNicModel import VirtualNicModel
from vCenterShell.pycommon.logger import getLogger

_logger = getLogger("vCenterShell")

#@todo need to be merged to Create Command (?)

class DestroyVirtualSwitchCommand(BaseCommand):

    def __init__(self, pv_service, data_retriever_service, switch_name, port_group_name):
        """
        :param pv_service: <pycommon.pyVmomiService obj>
        :param cs_retriever_service: <pycommon.CloudshellDataRetrieverService obj>
        """
        self.pvService = pv_service
        self.csRetrieverService = data_retriever_service
        self.switch_name = switch_name
        self.port_group_name = port_group_name

    def execute(self):
        #self.delete_port_group(vCenter, dvSwitchName, portGroupName)
        pass

    def delete_port_group(self, vCenter, dvSwitchName, portGroupName):
        #dv_switch = self.pyvmomi_service.find_network_by_name(si, dv_switch_path, dv_switch_name)
        pass