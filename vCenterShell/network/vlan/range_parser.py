from pyVmomi import vim


class VLanIdRangeParser(object):
    def __init__(self):
        pass

    def parse_vlan_id(self, vlan_id):

        if not vlan_id:
            raise Exception('VLAN should be a number or range in format 1-100')
        vlan_parts = str(vlan_id).split("-")
        if len(vlan_parts) > 2:
            raise Exception('VLAN should be a number or range in format 1-100')
        if len(vlan_parts) == 1:
            return [vim.NumericRange(start=int(vlan_parts[0]), end=int(vlan_parts[0]))]
        if len(vlan_parts) == 2:
            start_port = int(vlan_parts[0])
            end_port = int(vlan_parts[1])
            return [vim.NumericRange(start=start_port, end=end_port)]
