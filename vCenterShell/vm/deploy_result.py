

class DeployResult(object):
    def __init__(self, vm_name, uuid, vm_path):
        """
        :param str vm_name: The name of the virtual machine
        :param uuid uuid:   The UUID
        :param str vm_path: The full path to the VM including the vCenter resource name as the first part. The path
        parts are sapereted by '/'
        :return:
        """
        self.vm_name = vm_name
        self.uuid = uuid
        self.vm_path = vm_path
