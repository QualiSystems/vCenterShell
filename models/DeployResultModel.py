class DeployResult(object):
    def __init__(self, vm_name, vm_uuid, cloud_provider_resource_name, ip_regex, refresh_ip_timeout):
        """
        :param str vm_name: The name of the virtual machine
        :param uuid uuid: The UUID
        :param str cloud_provider_resource_name: The Cloud Provider resource name
        :param str ip_regex: Regex to filter IP address
        :param int refresh_ip_timeout: Timeout for Refresh IP
        :return:
        """
        self.vm_name = vm_name
        self.vm_uuid = vm_uuid
        self.cloud_provider_resource_name = cloud_provider_resource_name
        self.ip_regex = ip_regex
        self.refresh_ip_timeout = refresh_ip_timeout
