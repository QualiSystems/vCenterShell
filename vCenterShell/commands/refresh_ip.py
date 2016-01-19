import time


class RefreshIpCommand(object):
    TIMEOUT = 600

    def __init__(self, pyvmomi_service, cs_retriever_rervice, qualipy_helpers, resource_model_parser):
        self.qualipy_helpers = qualipy_helpers
        self.pyvmomi_service = pyvmomi_service
        self.cs_retriever_rervice = cs_retriever_rervice
        self.resource_model_parser = resource_model_parser

    def refresh_ip(self, si, vm_uuid, resource_name):
        """
        Refreshes IP address of virtual machine and updates Address property on the resource
        :param vm_uuid: UUID of Virtual Machine
        :param resource_name: Logical resource name to update address property on
        """

        api = self.qualipy_helpers.get_api_session()
        vcenter_resource_context = self.qualipy_helpers.get_resource_context_details()

        # vCenterResourceModel
        vcenter_resource_model = self.resource_model_parser.convert_to_resource_model(vcenter_resource_context)

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        # where vm. is the MOR of the VM
        # guest_primary_ipaddress = vm.guest.ipAddress

        ip = self._obtain_ip(vm, vcenter_resource_model.default_network)

        if ip is None:
            raise ValueError('IP address of VM {0} could not be obtained during {1} seconds',
                             resource_name,
                             self.TIMEOUT)

        api.UpdateResourceAddress(resource_name, ip)

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
