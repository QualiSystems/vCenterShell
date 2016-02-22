import time
import re
from common.logger import getLogger

logger = getLogger(__name__)


class RefreshIpCommand(object):
    TIMEOUT = 600
    IP_V4_PATTERN = re.compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

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

        time.sleep(20)

        api = self.qualipy_helpers.get_api_session()
        vcenter_resource_context = self.qualipy_helpers.get_resource_context_details()
        match_function = self._get_ip_match_function(api, resource_name)

        # vCenterResourceModel
        vcenter_resource_model = self.resource_model_parser.convert_to_resource_model(vcenter_resource_context)

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        if vm.guest.toolsStatus != 'toolsOk':
            raise ValueError('VMWare Tools status on VM {0} is {1}, while should be toolsOk'
                             .format(resource_name, vm.guest.toolsStatus))

        ip = self._obtain_ip(vm, vcenter_resource_model.default_network, match_function)

        if ip is None:
            raise ValueError('IP address of VM {0} could not be obtained during {1} seconds'
                             .format(resource_name, self.TIMEOUT))

        api.UpdateResourceAddress(resource_name, ip)

    @staticmethod
    def _get_ip_match_function(api, resource_name):

        logger.debug('Trying to obtain IP address for {0}'.format(resource_name))

        resource = api.GetResourceDetails(resource_name)
        ip_regexes = []
        ip_regex = '.*'
        if resource.VmDetails and resource.VmDetails[0].VmCustomParam:
            ip_regexes = [custom_param.Value for custom_param
                          in resource.VmDetails[0].VmCustomParam
                          if custom_param.Name == 'ip_regex']
        if ip_regexes:
            ip_regex = ip_regexes[0]
            logger.debug('Custom IP Regex to filter IP addresses {0}'.format(ip_regex))

        return re.compile(ip_regex).match

    def _obtain_ip(self, vm, default_network, match_function):
        time_elapsed = 0
        ip = None
        interval = self.TIMEOUT / 100
        while time_elapsed < self.TIMEOUT and ip is None:
            ips = RefreshIpCommand._get_ip_addresses(vm, default_network)
            if ips:
                print 'filtering ip by v4'
                logger.debug('Filtering IP adresses to limit to IP V4 {0}'.format(','.join(ips)))
                ips = RefreshIpCommand._select_ip_by_match(ips, RefreshIpCommand.IP_V4_PATTERN.match)
            if ips:
                print 'filtering ip by custom filter'
                logger.debug('Filtering IP adresses by custom IP Regex'.format(','.join(ips)))
                ips = RefreshIpCommand._select_ip_by_match(ips, match_function)
            if ips:
                ip = ips[0]
            time_elapsed += interval
            time.sleep(interval)
        return ip

    @staticmethod
    def _get_ip_addresses(vm, default_network):
        ips = []
        if not vm.guest.ipAddress:
            ips.append(vm.guest.ipAddress)
        for nic in vm.guest.net:
            if nic.network != default_network:
                for addr in nic.ipAddress:
                    ips.append(addr)
        return ips

    @staticmethod
    def _select_ip_by_match(ips, match_function):
        return [ip for ip in ips if match_function(ip)]
