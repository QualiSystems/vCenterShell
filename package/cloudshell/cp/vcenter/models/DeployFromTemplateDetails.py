from cloudshell.cp.vcenter.models.vCenterVMFromTemplateResourceModel import vCenterVMFromTemplateResourceModel


class DeployFromTemplateDetails(object):
    def __init__(self, template_resource_model, app_name):
        """
        :type template_resource_model:  vCenterVMFromTemplateResourceModel
        :type app_name: str
        :return:
        """
        self.template_resource_model = template_resource_model
        self.app_name = app_name
