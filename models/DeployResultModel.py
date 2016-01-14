class DeployResult(object):
    def __init__(self, vm_name, uuid, cloud_provider_resource_name):
        """
        :param str vm_name: The name of the virtual machine
        :param uuid uuid: The UUID
        :param str cloud_provider_resource_name: The Cloud Provider resource name
        :return:
        """
        self.vm_name = vm_name
        self.uuid = uuid
        self.cloud_provider_resource_name = cloud_provider_resource_name