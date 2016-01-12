class DvPortGroupNameGenerator(object):
    @staticmethod
    def generate_port_group_name(vlan_id):
        return 'VLAN ' + str(vlan_id)