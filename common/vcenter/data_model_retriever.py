

class VCenterDataModelRetriever(object):
    def __init__(self, quali_helpers, resource_parser, cs_data_retriever):
        self.quali_helpers = quali_helpers
        self.resource_parser = resource_parser
        self.cs_data_retriever = cs_data_retriever

    def get_vcenter_data_model(self):
        resource_context = self.quali_helpers.get_resource_context_details()
        session = self.quali_helpers.get_api_session()
        inventory_path_data = self.cs_data_retriever.getVCenterInventoryPathAttributeData(resource_context)
        vcenter_resource_name = inventory_path_data.vCenter_resource_name
        vcenter_resource_details = session.GetResourceDetails(vcenter_resource_name)
        return self.resource_parser.convert_to_resource_model(vcenter_resource_details)
