# -*- coding: utf-8 -*-

"""
The most common VM staff
"""

from pyVmomi import vim


def vm_reconfig_task(vm, device_change):
    """

    :param vm: <vim.vm> VM for which reconfigure Task will be started
    :param device_change: <list>
    :return:
    """
    config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
    task = vm.ReconfigVM_Task(config_spec)
    return task


def vm_get_network_by_name(vm, network_name):
    """
    Try to find Network scanning all attached to VM networks
    :param vm: <vim.vm>
    :param network_name: <str> name of network
    :return: <vim.vm.Network or None>
    """
    #return None
    for network in vm.network:
        if hasattr(network, "name") and network_name == network.name:
            return network
    return None