class VCenterConnectionDetails(object):
    """
    Defines Connection parameters
    """
    def __init__(self, host, username, password, port=443):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

    def as_dict(self):
        important_attributes = ("host", "username", "password", "port",)
        return {attribute_name: getattr(self, attribute_name) for attribute_name in important_attributes}
