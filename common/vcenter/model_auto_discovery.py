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
        all_items_in_vc = self.pv_service.get_all_items_in_vcenter(si, None)

        dc = self._validate_datacenter(si, all_items_in_vc, auto_attr, resource.attributes)
        dc_name = dc.name

        for key, value in resource.attributes.items():
            if key in [USER, PASSWORD]:
                continue
            validation_method = self._get_validation_method(key)
            validation_method(si, all_items_in_vc, auto_attr, dc_name, resource.attributes, key)

        return AutoLoadDetails([], auto_attr)

    @staticmethod
    def _get_default_from_vc_by_type_and_name(items_in_vc, vim_type, name=None):
        items = [item for item in items_in_vc
                 if isinstance(item, vim_type) and
                 (not name or item.name == name)]
        if len(items) == 1:
            return items[0]
        if len(items) > 1:
            return 'too many options'
        return 'not found'

    def _validate_datacenter(self, si, all_item_in_vc, auto_att, attributes):
        dc = self._validate_attribute(si, attributes, vim.Datacenter, DEFAULT_DATACENTER)
        if not dc:
            dc = self._get_default(all_item_in_vc, vim.Datacenter, DEFAULT_DATACENTER)
        auto_att.append(AutoLoadAttribute('', DEFAULT_DATACENTER, dc.name))
        return dc

    def _validate_attribute(self, si, attributes, vim_type, name, prefix=''):
        if name in attributes and attributes[name]:
            att_value = attributes[name]
            if prefix:
                att_value = '{0}/{1}'.format(prefix, att_value)

            obj = self.pv_service.find_item_in_path_by_type(si, att_value, vim_type)
            if not obj or isinstance(obj, str):
                raise KeyError('Could not find the {0}: {1}'.format(name, attributes[name]))
            return obj
        return False

    def _get_default(self, all_item_in_vc, vim_type, key):
        obj = self._get_default_from_vc_by_type_and_name(all_item_in_vc, vim_type)
        if isinstance(obj, str):
            raise Exception('Could not select {0} because: {1}'.format(key, obj))
        return obj

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

    def _validate_default_dvswitch(self, si, all_items_in_vc, auto_att, dc_name, attributes, key):
        d_switch = self._validate_attribute(si, attributes, vim.DistributedVirtualSwitch, key, dc_name)
        if not d_switch:
            d_switch = self._get_default(all_items_in_vc, vim.DistributedVirtualSwitch, key)
            d_name = self.get_full_name(dc_name, d_switch)
        else:
            d_name = attributes[key]
        auto_att.append(AutoLoadAttribute('', key, d_name))

    @staticmethod
    def _is_found(item, key):
        if not item:
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
    def _validate_empty(ai, all_items_in_vc, attributes, auto_attr, dc_name, key):
        return

    def _get_validation_method(self, name):
        if not name:
            return self._validate_empty()
        name = name.lower()
        name = name.split(' ')
        name = '_'.join(name)
        method_name = '_validate_{0}'.format(name)
        return getattr(self, method_name, self._validate_empty)

    @staticmethod
    def get_full_name(dc_name, managed_object, name=''):
        if name and name.find(dc_name) > -1:
            return name
        curr_path = managed_object.name
        if name:
            curr_path = '{0}/{1}'.format(managed_object.name, name)
        return VCenterAutoModelDiscovery.get_full_name(dc_name, managed_object.parent, curr_path)
