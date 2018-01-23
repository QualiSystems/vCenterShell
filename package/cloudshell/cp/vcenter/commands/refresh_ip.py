import re
import time

from retrying import retry

from cloudshell.cp.vcenter.commands.ip_result import IpResult, IpReason

from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from cloudshell.cp.vcenter.models.GenericDeployedAppResourceModel import GenericDeployedAppResourceModel


class RefreshIpCommand(object):
    INTERVAL = 5
    IP_V4_PATTERN = re.compile('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

    def __init__(self, pyvmomi_service, resource_model_parser, ip_manager):
        self.pyvmomi_service = pyvmomi_service
        self.resource_model_parser = resource_model_parser
        self.ip_manager = ip_manager

    def _do_not_run_on_static_vm(self, app_request_json):
        if app_request_json == '' or app_request_json is None:
            raise ValueError('This command cannot be executed on a Static VM.')

    def refresh_ip(self, si, logger, session, vcenter_data_model, resource_model, cancellation_context,
                   app_request_json):
        """
        Refreshes IP address of virtual machine and updates Address property on the resource

        :param vim.ServiceInstance si: py_vmomi service instance
        :param logger:
        :param vCenterShell.driver.SecureCloudShellApiSession session: cloudshell session
        :param GenericDeployedAppResourceModel resource_model: UUID of Virtual Machine
        :param VMwarevCenterResourceModel vcenter_data_model: the vcenter data model attributes
        :param cancellation_context:
        """
        self._do_not_run_on_static_vm(app_request_json=app_request_json)

        default_network = VMLocation.combine(
            [vcenter_data_model.default_datacenter, vcenter_data_model.holding_network])

        match_function = self.ip_manager.get_ip_match_function(
            self._get_ip_refresh_ip_regex(resource_model.vm_custom_params))

        timeout = self._get_ip_refresh_timeout(resource_model.vm_custom_params)

        vm = self.pyvmomi_service.find_by_uuid(si, resource_model.vm_uuid)

        ip_res = self.ip_manager.get_ip(vm, default_network, match_function, cancellation_context, timeout, logger)

        if ip_res.reason == IpReason.Timeout:
            raise ValueError('IP address of VM \'{0}\' could not be obtained during {1} seconds'
                             .format(resource_model.fullname, timeout))

        if ip_res.reason == IpReason.Success:
            self._update_resource_address_with_retry(session=session,
                                                     resource_name=resource_model.fullname,
                                                     ip_address=ip_res.ip_address)

            return ip_res.ip_address

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def _update_resource_address_with_retry(self, session, resource_name, ip_address):
        session.UpdateResourceAddress(resource_name, ip_address)

    @staticmethod
    def _get_ip_refresh_timeout(custom_params):
        timeout = RefreshIpCommand._get_custom_param(
            custom_params=custom_params,
            custom_param_name='refresh_ip_timeout')

        if not timeout:
            raise ValueError('Refresh IP Timeout is not set')

        return float(timeout)

    @staticmethod
    def _get_ip_refresh_ip_regex(custom_params):
        return RefreshIpCommand._get_custom_param(
            custom_params=custom_params,
            custom_param_name='ip_regex')

    @staticmethod
    def _get_custom_param(custom_params, custom_param_name):
        if not custom_params:
            return None

        custom_param_values = [custom_param.value for custom_param in custom_params
                               if custom_param.name == custom_param_name]

        if custom_param_values:
            return custom_param_values[0]
        return None