from pyVmomi import vim

from cloudshell.cp.vcenter.common.utilites.common_utils import represents_int


class VLanIdRangeParser(object):
    def __init__(self):
        pass

    @staticmethod
    def parse_vlan_id(vlan_type, vlan_id):
        if not vlan_type or not vlan_id:
            raise ValueError('vlan_id is empty')

        if vlan_type == 'Access':
            if represents_int(vlan_id):
                return int(vlan_id)
            raise KeyError('Access supports only int vlan id')
        elif vlan_type == 'Trunk':
            vlan_parts = str(vlan_id).split("-")
            if len(vlan_parts) > 2:
                raise Exception('VLAN should be a number or range in format 1-100')
            if len(vlan_parts) == 1:
                return [vim.NumericRange(start=int(vlan_parts[0]), end=int(vlan_parts[0]))]
            if len(vlan_parts) == 2:
                start_port = int(vlan_parts[0])
                end_port = int(vlan_parts[1])
                return [vim.NumericRange(start=start_port, end=end_port)]
        raise KeyError('vlan type: {0} is not supported'.format(vlan_type))
