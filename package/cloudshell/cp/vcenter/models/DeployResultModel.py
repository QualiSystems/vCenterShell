class DeployResult(object):
    def __init__(self, vm_name, vm_uuid, cloud_provider_resource_name, ip_regex, refresh_ip_timeout, auto_power_on,
                 auto_power_off, wait_for_ip, auto_delete, autoload):
        """
        :param str vm_name: The name of the virtual machine
        :param uuid uuid: The UUID
        :param str cloud_provider_resource_name: The Cloud Provider resource name
        :param str ip_regex: Regex to filter IP address
        :param int refresh_ip_timeout: Timeout for Refresh IP
        :param boolean auto_power_on:
        :param boolean auto_power_off:
        :param boolean wait_for_ip:
        :param boolean auto_delete:
        :param boolean autoload:
        :return:
        """
        self.vm_name = vm_name
        self.vm_uuid = vm_uuid
        self.cloud_provider_resource_name = cloud_provider_resource_name
        self.ip_regex = ip_regex
        self.refresh_ip_timeout = float(refresh_ip_timeout)
        self.auto_power_on = str(auto_power_on)
        self.auto_power_off = str(auto_power_off)
        self.wait_for_ip = str(wait_for_ip)
        self.auto_delete = str(auto_delete)
        self.autoload = str(autoload)
