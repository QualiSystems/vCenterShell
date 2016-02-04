import time


class RefreshIpCommand(object):
    TIMEOUT = 600

    def __init__(self, pyvmomi_service):
        self.pyvmomi_service = pyvmomi_service

    def refresh_ip(self, si, session, vm_uuid, resource_name, default_network):
        """
        Refreshes IP address of virtual machine and updates Address property on the resource

        :param vim.ServiceInstance si: py_vmomi service instance
        :param vCenterShell.driver.SecureCloudShellApiSession session: cloudshell session
        :param str vm_uuid: UUID of Virtual Machine
        :param str resource_name: Logical resource name to update address property on
        :param vim.Network default_network: the default network
        """

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        # where vm. is the MOR of the VM
        # guest_primary_ipaddress = vm.guest.ipAddress

        ip = self._obtain_ip(vm, default_network)

        if ip is None:
            raise ValueError('IP address of VM {0} could not be obtained during {1} seconds',
                             resource_name,
                             self.TIMEOUT)

        session.UpdateResourceAddress(resource_name, ip)

    def _obtain_ip(self, vm, default_network):
        time_elapsed = 0
        ip = None
        interval = self.TIMEOUT / 10
        while time_elapsed < self.TIMEOUT and ip is None:
            ips = RefreshIpCommand._get_ip_addresses(vm, default_network)
            if len(ips) >= 1:
                ip = ips[0]
            else:
                time_elapsed += interval
                time.sleep(interval)
        return ip

    @staticmethod
    def _get_ip_addresses(vm, default_network):
        ips = []
        for nic in vm.guest.net:
            if nic.network != default_network:
                for addr in nic.ipAddress:
                    ips.append(addr)
        return ips
