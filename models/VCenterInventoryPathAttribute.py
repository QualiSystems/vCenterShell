__author__ = 'shms'

class VCenterInventoryPathAttribute(object):

    def __init__(self, vCenter_resource_name, vm_folder):
        self.vCenter_resource_name = vCenter_resource_name
        self.vm_folder = vm_folder