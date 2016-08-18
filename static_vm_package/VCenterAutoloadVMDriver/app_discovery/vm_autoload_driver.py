from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.cp.vcenter.common.cloud_shell.driver_helper import CloudshellDriverHelper
from cloudshell.cp.vcenter.commands.load_vm import VMLoader
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from pyVim.connect import SmartConnect, Disconnect
from cloudshell.cp.vcenter.models.QualiDriverModels import AutoLoadAttribute, AutoLoadCommandContext, AutoLoadDetails
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.cp.vcenter.vm.ip_manager import VMIPManager
from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter

import jsonpickle

DOMAIN = 'Global'


class DeployAppOrchestrationDriver(object):
    def __init__(self):
        self.cs_helper = CloudshellDriverHelper()
        self.model_parser = ResourceModelParser()
        self.ip_manager = VMIPManager()
        self.task_waiter = SynchronousTaskWaiter()
        self.logger = get_qs_logger('VM AutoLoad')

    def get_inventory(self, context):
        """
        Will locate vm in vcenter and fill its uuid
        :type context: cloudshell.shell.core.context.ResourceCommandContext
        """
        vcenter_vm_name = context.resource.attributes['vCenter VM']
        vcenter_vm_name = vcenter_vm_name.replace('\\', '/')
        vcenter_name = context.resource.attributes['vCenter Name']

        self.logger.info('start autoloading vm_path: {0} on vcenter: {1}'.format(vcenter_vm_name, vcenter_name))

        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             DOMAIN)

        vcenter_api_res = session.GetResourceDetails(vcenter_name)
        vcenter_resource = self.model_parser.convert_to_vcenter_model(vcenter_api_res)

        si = None
        pv_service = pyVmomiService(SmartConnect, Disconnect, self.task_waiter)

        try:
            self.logger.info('connecting to vcenter ({0})'.format(vcenter_api_res.Address))
            si = self._get_connection_to_vcenter(pv_service, session, vcenter_resource, vcenter_api_res.Address)

            self.logger.info('loading vm uuid')
            vm_loader = VMLoader(pv_service)
            uuid = vm_loader.load_vm_uuid_by_name(si, vcenter_resource, vcenter_vm_name)
            self.logger.info('vm uuid: {0}'.format(uuid))
            self.logger.info('loading the ip of the vm')
            ip = self._try_get_ip(pv_service, si, uuid, vcenter_resource)
            if ip:
                session.UpdateResourceAddress(context.resource.name, ip)

        except Exception as e:
            self.logger.error(e)
            raise
        finally:
            if si:
                pv_service.disconnect(si)

        return self._get_auto_load_response(uuid, vcenter_name, context.resource)

    def _get_auto_load_response(self, uuid, vcenter_name, resource):
        vm_details = self._get_vm_details(uuid, vcenter_name, resource)
        autoload_atts = [AutoLoadAttribute('', 'VmDetails', vm_details)]
        return AutoLoadDetails([], autoload_atts)

    def _try_get_ip(self, pv_service, si, uuid, vcenter_resource):
        ip = None
        try:
            vm = pv_service.get_vm_by_uuid(si, uuid)
            ip_res = self.ip_manager.get_ip(vm,
                                            vcenter_resource.holding_network,
                                            self.ip_manager.get_ip_match_function(None),
                                            cancellation_context=None,
                                            timeout=None,
                                            logger=self.logger)
            if ip_res.ip_address:
                ip = ip_res.ip_address
        except Exception as e:
            self.logger.debug('Error while trying to load VM({0}) IP'.format(uuid))
        return ip

    @staticmethod
    def _get_vm_details(uuid, vcenter_name, resource):
        vm_details = ApiVmDetails()

        vm_details.UID = uuid
        vm_details.CloudProviderName = vcenter_name

        ip_regex = ApiVmCustomParam()
        ip_regex.Name = 'ip_regex'
        ip_regex.Value = resource.attributes['IP Regex']

        timeout = ApiVmCustomParam()
        timeout.Name = 'refresh_ip_timeout'
        timeout.Value = resource.attributes['Refresh IP Timeout']

        auto_power_off = ApiVmCustomParam()
        auto_power_off.Name = 'auto_power_off'
        auto_power_off.Value = resource.attributes['Auto Power Off']

        # AutoDelete is set to False to prevent accidental termination of imported VM's
        auto_delete = ApiVmCustomParam()
        auto_delete.Name = 'auto_delete'
        auto_delete.Value = 'False'

        vm_details.VmCustomParams.append(timeout)
        vm_details.VmCustomParams.append(ip_regex)
        vm_details.VmCustomParams.append(auto_power_off)
        vm_details.VmCustomParams.append(auto_delete)

        str_vm_details = jsonpickle.encode(vm_details, unpicklable=False)
        return str_vm_details

    def _get_connection_to_vcenter(self, pv_service, session, vcenter_resource, address):
        password = self._decrypt_password(session, vcenter_resource.password)
        si = pv_service.connect(address,
                                vcenter_resource.user,
                                password,
                                443)
        return si

    @staticmethod
    def _decrypt_password(session, password):
        return session.DecryptPassword(password).Value


class ApiVmDetails(object):
    def __init__(self):
        self.CloudProviderName = ''
        self.UID = ''
        self.VmCustomParams = []


class ApiVmCustomParam(object):
    def __init__(self):
        self.Name = ''
        self.Value = ''
