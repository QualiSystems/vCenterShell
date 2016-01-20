

class VCenterDataModelRetriever(object):
    def __init__(self, quali_helpers, resource_parser):
        self.quali_helpers = quali_helpers
        self.resource_parser = resource_parser

    def get_vcenter_data_model(self):
        resource_context = self.quali_helpers.get_resource_context_details()
        return self.resource_parser.convert_to_resource_model(resource_context)
