from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.shell.core.driver_context import ApiVmDetails, ApiVmCustomParam

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
        self.pv_service = pyVmomiService(SmartConnect, Disconnect, self.task_waiter)

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

        try:
            self.logger.info('connecting to vcenter ({0})'.format(vcenter_api_res.Address))
            si = self._get_connection_to_vcenter(self.pv_service, session, vcenter_resource, vcenter_api_res.Address)

            self.logger.info('loading vm uuid')
            vm_loader = VMLoader(self.pv_service)
            uuid = vm_loader.load_vm_uuid_by_name(si, vcenter_resource, vcenter_vm_name)
            self.logger.info('vm uuid: {0}'.format(uuid))
            self.logger.info('loading the ip of the vm')
            ip = self._try_get_ip(self.pv_service, si, uuid, vcenter_resource)
            if ip:
                session.UpdateResourceAddress(context.resource.name, ip)

        except Exception:
            self.logger.exception("Get inventory command failed")
            raise
        finally:
            if si:
                self.pv_service.disconnect(si)

        return self._get_auto_load_response(uuid, vcenter_name, context.resource)

    def _get_auto_load_response(self, uuid, vcenter_name, resource):
        vm_details = self._get_vm_details(uuid, vcenter_name, resource)
        # return vm_details
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
        except Exception:
            self.logger.debug('Error while trying to load VM({0}) IP'.format(uuid), exc_info=True)
        return ip

    @staticmethod
    def _get_vm_details(uuid, vcenter_name, resource):

        vm_details = ApiVmDetails()
        vm_details.UID = uuid
        vm_details.CloudProviderName = vcenter_name
        vm_details.VmCustomParams = []
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
