import re

import time

from common.logger import getLogger

logger = getLogger(__name__)


class RefreshIpCommand(object):
    TIMEOUT = 600
    IP_V4_PATTERN = re.compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

    def __init__(self, pyvmomi_service, resource_model_parser):
        self.pyvmomi_service = pyvmomi_service
        self.resource_model_parser = resource_model_parser

    def refresh_ip(self, si, session, vm_uuid, resource_name, default_network):
        """
        Refreshes IP address of virtual machine and updates Address property on the resource

        :param vim.ServiceInstance si: py_vmomi service instance
        :param vCenterShell.driver.SecureCloudShellApiSession session: cloudshell session
        :param str vm_uuid: UUID of Virtual Machine
        :param str resource_name: Logical resource name to update address property on
        :param vim.Network default_network: the default network
        """
        match_function = self._get_ip_match_function(session, resource_name)

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        if vm.guest.toolsStatus != 'toolsOk':
            raise ValueError('VMWare Tools status on VM {0} is {1}, while should be toolsOk'
                             .format(resource_name, vm.guest.toolsStatus))

        ip = self._obtain_ip(vm, default_network, match_function)

        if ip is None:
            raise ValueError('IP address of VM {0} could not be obtained during {1} seconds'
                             .format(resource_name, self.TIMEOUT))

        session.UpdateResourceAddress(resource_name, ip)

    @staticmethod
    def _get_ip_match_function(session, resource_name):

        logger.debug('Trying to obtain IP address for {0}'.format(resource_name))

        resource = session.GetResourceDetails(resource_name)
        ip_regexes = []
        ip_regex = '.*'

        if resource.VmDetails and resource.VmDetails.VmCustomParams:
            params = resource.VmDetails.VmCustomParams if isinstance(resource.VmDetails.VmCustomParams, list) \
                else [resource.VmDetails.VmCustomParams]
            ip_regexes = [custom_param.Value for custom_param
                          in params
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
                if ip:
                    return ip
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
