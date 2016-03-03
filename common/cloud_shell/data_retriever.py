from models.VCenterConnectionDetails import VCenterConnectionDetails


class CloudshellDataRetrieverService:
    def __init__(self):
        pass

    PATH_DELIMITER = "/"

    def getVCenterConnectionDetails(self, session, vCenter_resource_details):
        """
        Return a dictionary with vCenter connection details. Methods receives a ResourceDetails object of a vCenter resource
        and retrieves the connection details from its attributes.

        :param vCenter_resource_details:   the ResourceDetails object of a vCenter resource
        :param session:                    the cloushell api session, its needed in order to decrypt the password
        """


