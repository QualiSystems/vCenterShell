class vCenterCloneVMFromVMResourceModel(object):
    def __init__(self):
        self.vcenter_name = ''
        self.vcenter_vm = ''
        self.vm_cluster = ''
        self.vm_storage = ''
        self.ip_regex = ''
        self.vm_resource_pool = ''
        self.vm_location = ''
        self.auto_power_on = True
        self.auto_power_off = True
        self.wait_for_ip = True
        self.auto_delete = True
        self.autoload = True
        self.refresh_ip_timeout = 0
