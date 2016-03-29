

class vCenterVMFromImageResourceModel(object):
    def __init__(self):
        self.vcenter_name = ''
        self.vcenter_image = ''
        self.vcenter_image_arguments = ''
        self.vm_cluster = ''
        self.vm_storage = ''
        self.vm_resource_pool = ''
        self.vm_location = ''
        self.auto_power_on = True
        self.auto_power_off = True
        self.wait_for_ip = True
        self.auto_delete = True
        self.autoload = True
        self.ip_regex = ''
        self.default_datacenter = ''
        self.refresh_ip_timeout = 0
