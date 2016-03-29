import re
import time

from cloudshell.cp.vcenter.commands.ip_result import IpResult, IpReason

from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation


class RefreshIpCommand(object):
    INTERVAL = 5
    IP_V4_PATTERN = re.compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

    def __init__(self, pyvmomi_service, resource_model_parser):
        self.pyvmomi_service = pyvmomi_service
        self.resource_model_parser = resource_model_parser

    def refresh_ip(self, si, logger, session, vcenter_data_model, vm_uuid, resource_name, cancellation_context):
        """
        Refreshes IP address of virtual machine and updates Address property on the resource

        :param vim.ServiceInstance si: py_vmomi service instance
        :param logger:
        :param vCenterShell.driver.SecureCloudShellApiSession session: cloudshell session
        :param str vm_uuid: UUID of Virtual Machine
        :param str resource_name: Logical resource name to update address property on
        :param VMwarevCenterResourceModel vcenter_data_model: the vcenter data model attributes
        :param cancellation_context:
        """
        default_network = VMLocation.combine([vcenter_data_model.default_datacenter, vcenter_data_model.holding_network])

        resource = session.GetResourceDetails(resource_name)

        match_function = self._get_ip_match_function(resource)

        timeout = self._get_ip_refresh_timeout(resource)

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        if vm.guest.toolsStatus == 'toolsNotInstalled':
            logger.warning('VMWare Tools status on virtual machine \'{0}\' are not installed'.format(resource_name))
            return None

        ip_result = self._obtain_ip(vm, default_network, match_function, cancellation_context, timeout, logger)

        if ip_result.reason == IpReason.Timeout:
            raise ValueError('IP address of VM \'{0}\' could not be obtained during {1} seconds'
                             .format(resource_name, timeout))

        if ip_result.reason == IpReason.Success:
            session.UpdateResourceAddress(resource_name, ip_result.ip_address)

            return ip_result.ip_address

    @staticmethod
    def _get_ip_match_function(resource):
        ip_regex = RefreshIpCommand._get_custom_param(
            resource=resource,
            custom_param_name='ip_regex')

        ip_regex = ip_regex or '.*'

        return re.compile(ip_regex).match

    @staticmethod
    def _get_ip_refresh_timeout(resource):
        timeout = RefreshIpCommand._get_custom_param(
            resource=resource,
            custom_param_name='refresh_ip_timeout')

        if not timeout:
            raise ValueError('Refresh IP Timeout is not set')

        return float(timeout)

    @staticmethod
    def _get_custom_param(resource, custom_param_name):
        custom_param_values = []
        vm_details = resource.VmDetails
        if vm_details and hasattr(vm_details, 'VmCustomParams') and vm_details.VmCustomParams:
            custom_params = vm_details.VmCustomParams
            params = custom_params if isinstance(custom_params, list) else [custom_params]
            custom_param_values = [custom_param.Value for custom_param
                                   in params
                                   if custom_param.Name == custom_param_name]

        if custom_param_values:
            return custom_param_values[0]
        return None

    def _obtain_ip(self, vm, default_network, match_function, cancellation_context, timeout, logger):
        time_elapsed = 0
        ip = None
        interval = self.INTERVAL
        while time_elapsed < timeout and ip is None:
            if cancellation_context.is_cancelled:
                return IpResult(ip, IpReason.Cancelled)
            ips = RefreshIpCommand._get_ip_addresses(vm, default_network)
            if ips:
                logger.debug('Filtering IP adresses to limit to IP V4 \'{0}\''.format(','.join(ips)))
                ips = RefreshIpCommand._select_ip_by_match(ips, RefreshIpCommand.IP_V4_PATTERN.match)
            if ips:
                logger.debug('Filtering IP adresses by custom IP Regex'.format(','.join(ips)))
                ips = RefreshIpCommand._select_ip_by_match(ips, match_function)
            if ips:
                ip = ips[0]
                if ip:
                    return IpResult(ip, IpReason.Success)
            time_elapsed += interval
            time.sleep(interval)
        return IpResult(ip, IpReason.Timeout)

    @staticmethod
    def _get_ip_addresses(vm, default_network):
        ips = []
        if vm.guest.ipAddress:
            ips.append(vm.guest.ipAddress)
        for nic in vm.guest.net:
            if nic.network != default_network:
                for addr in nic.ipAddress:
                    if addr:
                        ips.append(addr)
        return ips

    @staticmethod
    def _select_ip_by_match(ips, match_function):
        return [ip for ip in ips if match_function(ip)]
