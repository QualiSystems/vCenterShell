# -*- coding: utf-8 -*-

"""
The most common VM staff
"""

from pyVmomi import vim


def vm_reconfig_task(vm, device_change):
    config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
    task = vm.ReconfigVM_Task(config_spec)
    return task
