from cloudshell.cp.vcenter.models.vCenterVMFromImageResourceModel import vCenterVMFromImageResourceModel


class DeployFromImageDetails(object):
    def __init__(self, image_params, app_name):
        """
        :type image_params:  vCenterVMFromImageResourceModel
        :type app_name: str
        :return:
        """
        self.image_params = image_params
        self.app_name = app_name