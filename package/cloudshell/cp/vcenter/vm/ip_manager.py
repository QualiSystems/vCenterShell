import time
import re
from cloudshell.cp.vcenter.commands.ip_result import IpReason, IpResult


class VMIPManager(object):
    INTERVAL = 5
    IP_V4_PATTERN = re.compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

    def get_ip(self, vm, default_network, match_function, cancellation_context, timeout, logger,
               guest_tools_timeout=None):
        self._validate_vmware_tools_installed(logger, vm, guest_tools_timeout or 300000)
        ip = None
        reason = IpReason.Success
        if not timeout:
            ip = self._obtain_ip(vm, default_network, match_function, logger)
            if not ip:
                reason = IpReason.NotFound
        else:
            time_elapsed = 0
            interval = self.INTERVAL
            while time_elapsed < timeout and not ip:
                if cancellation_context.is_cancelled:
                    reason = IpReason.Cancelled
                    break
                ip = self._obtain_ip(vm, default_network, match_function, logger)
                if not ip:
                    time_elapsed += interval
                    time.sleep(interval)

            if time_elapsed >= timeout:
                reason = IpReason.Timeout

        return IpResult(ip, reason)

    @staticmethod
    def get_ip_match_function(ip_regex=None):
        ip_regex = ip_regex or '.*'
        return re.compile(ip_regex).match

    def _obtain_ip(self, vm, default_network, match_function, logger):
        ip = None
        ips = self._get_ip_addresses(vm, default_network)

        if ips:
            logger.debug('Filtering IP adresses to limit to IP V4 \'{0}\''.format(','.join(ips)))
            ips = self._select_ip_by_match(ips, self.IP_V4_PATTERN.match)
        if ips:
            logger.debug('Filtering IP adresses by custom IP Regex'.format(','.join(ips)))
            ips = self._select_ip_by_match(ips, match_function)

        # select the first on that found
        if ips:
            ip = ips[0]

        return ip

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

    @staticmethod
    def _validate_vmware_tools_installed(logger, vm, guest_tools_timeout=300000):
        sleep = 1
        while guest_tools_timeout > 0:
                if vm.guest.toolsStatus == 'toolsNotInstalled':
                    msg = 'VMWare Tools status on virtual machine \'{0}\' are not installed'.format(vm.name)
                    logger.warning(msg)
                    time.sleep(sleep)
                    guest_tools_timeout -= sleep * 1000
                    sleep *= 2 # exponential backoff
                else:
                    return True
        raise ValueError(msg)
