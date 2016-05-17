import re
import time

from cloudshell.cp.vcenter.commands.ip_result import IpResult, IpReason

from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation


class RefreshIpCommand(object):
    INTERVAL = 5
    IP_V4_PATTERN = re.compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

    def __init__(self, pyvmomi_service, resource_model_parser, ip_manager):
        self.pyvmomi_service = pyvmomi_service
        self.resource_model_parser = resource_model_parser
        self.ip_manager = ip_manager

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

        match_function = self.ip_manager.get_ip_match_function(self._get_ip_refresh_ip_regex(resource))

        timeout = self._get_ip_refresh_timeout(resource)

        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        ip_res = self.ip_manager.get_ip(vm, default_network, match_function, cancellation_context, timeout, logger)

        if ip_res.reason == IpReason.Timeout:
            raise ValueError('IP address of VM \'{0}\' could not be obtained during {1} seconds'
                             .format(resource_name, timeout))

        if ip_res.reason == IpReason.Success:
            session.UpdateResourceAddress(resource_name, ip_res.ip_address)

            return ip_res.ip_address

    @staticmethod
    def _get_ip_refresh_timeout(resource):
        timeout = RefreshIpCommand._get_custom_param(
            resource=resource,
            custom_param_name='refresh_ip_timeout')

        if not timeout:
            raise ValueError('Refresh IP Timeout is not set')

        return float(timeout)

    @staticmethod
    def _get_ip_refresh_ip_regex(resource):
        return RefreshIpCommand._get_custom_param(
            resource=resource,
            custom_param_name='ip_regex')

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


