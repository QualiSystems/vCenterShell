

class CloudshellResourceRemover(object):
    def __init__(self, quali_helpers):
        self.helpers = quali_helpers

    def remove_resource(self, resource_full_name):
        """
        removes resource from session
        :type resource_full_name: str
        """
        session = self.helpers.get_api_session()
        session.DeleteResource(resource_full_name)
