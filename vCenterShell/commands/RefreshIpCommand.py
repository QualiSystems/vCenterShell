import qualipy.scripts.cloudshell_scripts_helpers as helpers
import time

TIMEOUT = 600


class RefreshIpCommand(object):
    def __init__(self, pyvmomi_service, cs_retriever_rervice, qualipy_helpers, resource_model_parser):
        self.qualipy_helpers = qualipy_helpers
        self.pyvmomi_service = pyvmomi_service
        self.cs_retriever_rervice = cs_retriever_rervice
        self.resource_model_parser = resource_model_parser

    def refresh_ip(self, vm_uuid, resource_name):
        """
        Refreshes IP address of virtual machine and updates Address property on the resource
        :param vm_uuid: UUID of Virtual Machine
        :param resource_name: Logical resource name to update address property on
        """

        session = self.qualipy_helpers.helpers.get_api_session()
        resource_details = session.GetResourceDetails(resource_name)

        # GenericAppModelResourceModel
        vm_resource = self.resource_model_parser.convert_to_resource_model(resource_details)

        resource_context = self.qualipy_helpers.get_resource_context_details()
        connection_details = self.cs_retriever_rervice.getVCenterConnectionDetails(resource_context)

        si = self.pyvmomi_service.connect(connection_details.host, connection_details.username,
                                          connection_details.password,
                                          connection_details.port)

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        # where vm. is the MOR of the VM
        # guest_primary_ipaddress = vm.guest.ipAddress

        ip = self._obtain_ip(vm, vm_resource)

        if ip is None:
            raise ValueError('IP address of VM {0} could not be obtained during {1} seconds', resource_name, TIMEOUT)

        pass

    def _obtain_ip(self, vm, vm_resource):
        time_elapsed = 0
        ip = None
        interval = TIMEOUT / 10
        while time_elapsed < TIMEOUT and ip is None:
            ips = self._get_ip_addresses(vm, vm_resource)
            if len(ips) >= 1:
                ip = ips[0]
            else:
                time_elapsed += interval
                time.sleep(interval)
        return ip

    def _get_ip_addresses(self, vm, vm_resource):
        ips = []
        for nic in vm.guest.net:
            if nic.network != vm_resource.default_network:
                for addr in nic.ipAddress:
                    ips.append(addr)
        return ips
