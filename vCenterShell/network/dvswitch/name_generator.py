class DvPortGroupNameGenerator(object):
    def generate_port_group_name(self, vlan_id):
        return 'VLAN ' + str(vlan_id)