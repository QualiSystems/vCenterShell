# -*- coding: utf-8 -*-
"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info
"""

from pyVmomi import vim
from pycommon.pyVmomiService import *
import qualipy.scripts.cloudshell_scripts_helpers as helpers

# from models.VCenterConnectionDetails import VCenterConnectionDetails
# from pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
# from pycommon.pyVmomiService import pyVmomiService


#from .VirtualSwitchCommon import connection_details_by_vm_name
from .VirtualSwitchCommon import VirtualSwitchCommandBase

from pycommon.logger import getLogger

_logger = getLogger("vCenterShell")


class VirtualSwitchFromMachineRevoker(VirtualSwitchCommandBase):

    def __init__(self,
                 pyvmomi_service,
                 connection_retriever,
                 synchronous_task_waiter):
        super(VirtualSwitchFromMachineRevoker, self).__init__(pyvmomi_service,
                                                              connection_retriever,
                                                              synchronous_task_waiter)

    def revoke(self,
                vlan_id,
                vm_name,
                vm_uuid,
                dv_switch_path,
                dv_switch_name,
                virtual_machine_path):
        if not self.is_vcenter_connected():
            self.vcenter_connect(self.get_connection_details(vm_name))
        pass

    def execute(self):
        pass
