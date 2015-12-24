from pyVmomi import vim


class VlanSpecFactory(object):
    def __init__(self):
        self.dvsVlanSpec = {
            'Access': vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec(),
            'Trunk': vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec()
        }

    def get_vlan_spec(self, vlan_spec_name):
        """
        Returns an instance of vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec according to name:
        'VLAN', 'VLAN Trunking', 'Private VLAN'
        :param vlan_spec_name: str
        :return:  vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec
        """
        return self.dvsVlanSpec[vlan_spec_name]