

class CloudshellResourceRemover(object):
    def remove_resource(self, session, resource_full_name):
        """
        removes resource from session
        :type resource_full_name: str
        """
        session.DeleteResource(resource_full_name)
