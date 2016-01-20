class VCenterTemplateModel(object):

    def __init__(self, vcenter_resource_name, vm_folder, template_name):
        self.vCenter_resource_name = vcenter_resource_name
        self.vm_folder = vm_folder
        self.template_name = template_name


