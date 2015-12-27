# -*- coding: utf-8 -*-
"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info

@see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.DistributedVirtualSwitch.html
"""

from pyVmomi import vim
from pycommon.pyVmomiService import *

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

    def execute(self):
        pass

    def revoke(self,
            vm_name,
            vm_uuid,
            dv_switch_path,
            dv_switch_name,
            virtual_machine_path):
        if not self.is_vcenter_connected():
            self.vcenter_connect(self.get_connection_details(vm_name))

        _logger.debug("Revoking ALL Interfaces from VM '{}'".format(vm_name))

        vm = self.pyvmomi_service.find_by_uuid(self.si, virtual_machine_path, vm_uuid)
        dv_switch_NOTUSED_FOR_NOW = self.pyvmomi_service.find_network_by_name(self.si, dv_switch_path, dv_switch_name)
        return self.remove_all_interfaces_from_vm(vm)

    def remove_all_interfaces_from_vm(self, virtual_machine):
        """
        @see https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.VirtualMachine.html#reconfigure
        :param virtual_machine: <vim.vm object>
        :return:
        """
        device_change = []
        for device in virtual_machine.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard):
                nicspec = vim.vm.device.VirtualDeviceSpec()
                device_change.append(nicspec)

        config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
        task = virtual_machine.ReconfigVM_Task(config_spec)
        logger.info("Virtual Machine remove ALL Interfaces task STARTED")
        return self.synchronous_task_waiter.wait_for_task(task)
