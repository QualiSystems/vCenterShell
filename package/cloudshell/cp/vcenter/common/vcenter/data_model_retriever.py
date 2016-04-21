from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel


class VCenterDataModelRetriever(object):
    def __init__(self, resource_model_parser):
        """
        :param ResourceModelParser resource_model_parser:
        :return:
        """
        self.resource_model_parser = resource_model_parser

    def get_vcenter_data_model(self, api, vcenter_name):
        """
        :param api:
        :param str vcenter_name:
        :rtype:  VMwarevCenterResourceModel
        """
        if not vcenter_name:
            raise ValueError('VMWare vCenter name is empty')
        vcenter_instance = api.GetResourceDetails(vcenter_name)
        vcenter_resource_model = self.resource_model_parser.convert_to_vcenter_model(vcenter_instance)
        return vcenter_resource_model
