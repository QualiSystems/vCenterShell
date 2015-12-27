class vCenterResourceModel(object):
    def __init__(self, vcenter_url, user, password, domain_selector, default_dvswitch_name, default_dvswitch_path,
                 default_port_group_path):
        self.vcenter_url = vcenter_url
        self.user = user
        self.password = password
        self.domain_selector = domain_selector
        self.default_dvswitch_name = default_dvswitch_name
        self.default_dvswitch_path = default_dvswitch_path
        self.default_port_group_path = default_port_group_path
