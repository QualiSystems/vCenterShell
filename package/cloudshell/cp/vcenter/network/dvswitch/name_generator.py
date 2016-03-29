QS_NAME_PREFIX = 'QS'
VLAN = 'VLAN'
NAME_FORMAT = '{0}_{1}_{2}_{3}'


class DvPortGroupNameGenerator(object):
    @staticmethod
    def generate_port_group_name(vlan_id, vlan_type):
        return NAME_FORMAT.format(QS_NAME_PREFIX, VLAN, str(vlan_id), str(vlan_type))

    @staticmethod
    def is_generated_name(name):
        return str(name).startswith(QS_NAME_PREFIX)
