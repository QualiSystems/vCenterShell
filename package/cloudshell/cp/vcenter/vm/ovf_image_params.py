import cloudshell

class OvfImageParams(object):
    def __init__(self):
        self.connectivity = None  # type: cloudshell.cp.vcenter.models.VCenterConnectionDetails
        self.datacenter = None  # type: str
        self.cluster = None  # type: str
        self.resource_pool = None  # type: str
        self.vm_name = None  # type: str
        self.datastore = None  # type: str
        self.image_url = None  # type: str
        self.user_arguments = None  # type: list
        self.vm_folder = None  # type: str
        self.power_on = False  # type: bool
        self.vcenter_name = False  # type: bool
