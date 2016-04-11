MAX_DVSWITCH_LENGTH = 60
QS_NAME_PREFIX = 'QS'
VLAN = 'VLAN'
NAME_FORMAT = '{0}_{1}_{2}_{3}_{4}'


class DvPortGroupNameGenerator(object):
    @staticmethod
    def generate_port_group_name(dv_switch_name, vlan_id, vlan_type):
        dv_switch_name = dv_switch_name[:MAX_DVSWITCH_LENGTH]
        return NAME_FORMAT.format(QS_NAME_PREFIX, dv_switch_name, VLAN, str(vlan_id), str(vlan_type))

    @staticmethod
    def is_generated_name(name):
        return str(name).startswith(QS_NAME_PREFIX)
