from pyVim.connect import SmartConnect, Disconnect

from pyVmomi import vim
from common.cloud_shell.driver_helper import CloudshellDriverHelper
from common.model_factory import ResourceModelParser
from common.vcenter.vmomi_service import pyVmomiService
from models.QualiDriverModels import AutoLoadDetails, AutoLoadAttribute
from models.VCenterConnectionDetails import VCenterConnectionDetails
from models.VMwarevCenterResourceModel import VMwarevCenterResourceModel

ADDRESS = 'address'
USER = 'User'
PASSWORD = 'Password'
DEFAULT_DVSWITCH = 'Default dvSwitch'
DEFAULT_DATACENTER = 'Default Datacenter'
DEFAULT_PORT_GROUP_LOCATION = 'Default Port Group Location'
EXECUTION_SERVER_SELECTOR = 'Execution Server Selector'
HOLDING_NETWORK = 'Holding Network'
OVF_TOOL_PATH = 'OVF Tool Path'
PROMISCUOUS_MODE = 'Promiscuous Mode'
SHUTDOWN_METHOD = 'Shutdown Method'
VM_CLUSTER = 'VM Cluster'
VM_LOCATION = 'VM Location'
VM_RESOURCE_POOL = 'VM Resource Pool'
VM_STORAGE = 'VM Storage'


class VCenterAutoModelDiscovery(object):
    def __init__(self):
        self.parser = ResourceModelParser()
        self.pv_service = pyVmomiService(SmartConnect, Disconnect)
        self.cs_helper = CloudshellDriverHelper()

    def validate_and_discover(self, context):
        """
        :type context: models.QualiDriverModels.AutoLoadCommandContext
        """
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             None)
        self._check_if_attribute_not_empty(context.resource, ADDRESS)
        resource = context.resource
        auto_attr = []

        si = self._check_if_vcenter_user_pass_valid(context, session, resource.attributes)
        self._check_if_attribute_not_empty(resource.attributes, DEFAULT_DATACENTER)

        dc = self.pv_service.find_datacenter_by_name(si, '', resource.attributes[DEFAULT_DATACENTER])

        for key, value in resource.attributes.items():
            if key in [USER, PASSWORD]:
                continue
            validation_method = self._get_validation_method(key)
            discovered = validation_method(si, key, value)
            if discovered:
                auto_attr.append(discovered)

        return AutoLoadDetails([resource], auto_attr)

    def _check_if_vcenter_user_pass_valid(self, context, session, attributes):
        self._check_if_attribute_not_empty(attributes, USER)
        self._check_if_attribute_not_empty(attributes, PASSWORD)
        connection_details = self._get_connection_details(session,
                                                          attributes[PASSWORD],
                                                          attributes[USER],
                                                          context.resource.address)
        try:
            si = self.pv_service.connect(connection_details.host,
                                         connection_details.username,
                                         connection_details.password,
                                         connection_details.port)
        except Exception:
            raise KeyError('could not connect to the vcenter: {0}, with the given credentials ({1})'.format(
                connection_details.host,
                connection_details.username))
        return si

    def _validate_default_dvswitch(self, si, key, value):
        if value:
            dvswitch = self.pv_service.get_network_by_full_name(si, value)
            self._is_found(dvswitch, key)
        else:
            dvswitch = self.pv_service.get_default_from_vcenter_by_type(si, vim.DistributedVirtualSwitch, False)
            self._is_found(dvswitch, key)
            return AutoLoadAttribute(key, key, dvswitch.name)

    @staticmethod
    def _is_found(dvswitch, key):
        if not dvswitch:
            raise KeyError('The {0} could not be found in the given vCenter'.format(key))

    @staticmethod
    def _get_connection_details(session, password, user, address):
        password = session.DecryptPassword(password).Value
        return VCenterConnectionDetails(address, user, password)

    @staticmethod
    def _check_if_attribute_not_empty(attributes, name):
        if not ((hasattr(attributes, name) and getattr(attributes, name)) or
                    (isinstance(attributes, dict) and name in attributes and attributes[name])):
            raise KeyError('{0} cannot be empty'.format(name))

    @staticmethod
    def _validate_empty(si, key, value):
        return

    def _get_validation_method(self, name):
        if not name:
            return self._validate_empty()
        name = name.lower()
        name = name.split(' ')
        name = '_'.join(name)
        method_name = '_validate_{0}'.format(name)
        return getattr(self, method_name, self._validate_empty)
