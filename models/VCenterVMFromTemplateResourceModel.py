class vCenterVMFromTemplateResourceModel(object):
    def __init__(self, domain_selector, template, location, cloud_provider):
        self.cloud_provider = cloud_provider
        self.location = location
        self.template = template
        self.domain_selector = domain_selector
