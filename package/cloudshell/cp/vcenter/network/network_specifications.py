"""
The most common network/Distributed Virtual Switch staff
"""

from pyVmomi import vim

def network_is_standard(network):
    return isinstance(network, vim.Network) or (network and str(network).startswith("vim.Network:"))


def network_is_portgroup(network):
    return isinstance(network, vim.dvs.DistributedVirtualPortgroup) \
           or network and str(network).startswith("vim.dvs.VmwareDistributedVirtualSwitch:")

