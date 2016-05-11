import collections

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from cloudshell.cp.vcenter.common.utilites.context_based_logger_factory import ContextBasedLoggerFactory
from cloudshell.cp.vcenter.models.QualiDriverModels import AutoLoadDetails, AutoLoadAttribute
from cloudshell.cp.vcenter.models.VCenterConnectionDetails import VCenterConnectionDetails

from cloudshell.cp.vcenter.common.cloud_shell.driver_helper import CloudshellDriverHelper
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService

DOMAIN = 'Global'
ADDRESS = 'address'
USER = 'User'
PASSWORD = 'Password'
DEFAULT_DVSWITCH = 'Default dvSwitch'
DEFAULT_DATACENTER = 'Default Datacenter'
EXECUTION_SERVER_SELECTOR = 'Execution Server Selector'
HOLDING_NETWORK = 'Holding Network'
OVF_TOOL_PATH = 'OVF Tool Path'
SHUTDOWN_METHOD = 'Shutdown Method'
VM_CLUSTER = 'VM Cluster'
VM_LOCATION = 'VM Location'
VM_RESOURCE_POOL = 'VM Resource Pool'
VM_STORAGE = 'VM Storage'
SHUTDOWN_METHODS = ['soft', 'hard']


class VCenterAutoModelDiscovery(object):
    def __init__(self):
        self.parser = ResourceModelParser()
        self.pv_service = pyVmomiService(SmartConnect, Disconnect)
        self.cs_helper = CloudshellDriverHelper()
        self.context_based_logger_factory = ContextBasedLoggerFactory()

    def validate_and_discover(self, context):
        """
        :type context: models.QualiDriverModels.AutoLoadCommandContext
        """
        logger = self.context_based_logger_factory.create_logger_for_context(
            logger_name='vCenterShell',
            context=context)

        logger.info('Autodiscovery started')

        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             DOMAIN)
        self._check_if_attribute_not_empty(context.resource, ADDRESS)
        resource = context.resource
        auto_attr = []
        si = self._check_if_vcenter_user_pass_valid(context, session, resource.attributes)
        if not si:
            error_message = 'Could not connect to the vCenter: {0}, with given credentials'\
                .format(context.resource.address)
            logger.error(error_message)
            raise ValueError(error_message)
        all_dc = self.pv_service.get_all_items_in_vcenter(si, vim.Datacenter)

        dc = self._validate_datacenter(si, all_dc, auto_attr, resource.attributes)

        all_items_in_dc = self.pv_service.get_all_items_in_vcenter(si, None, dc)

        dc_name = dc.name

        for key, value in resource.attributes.items():
            if key in [USER, PASSWORD, DEFAULT_DATACENTER, VM_CLUSTER]:
                continue
            validation_method = self._get_validation_method(key)
            validation_method(si, all_items_in_dc, auto_attr, dc_name, resource.attributes, key)

        logger.info('Autodiscovery completed')

        return AutoLoadDetails([], auto_attr)

    @staticmethod
    def _get_default_from_vc_by_type_and_name(items_in_vc, vim_type, name=None):
        items = []
        if not isinstance(vim_type, collections.Iterable):
            vim_type = [vim_type]
        for item in items_in_vc:
            if item.name == name:
                return item

            item_type = type(item)
            if [t for t in vim_type if item_type is t]:
                items.append(item)

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

            obj = self.pv_service.get_folder(si, att_value)
            if not obj or isinstance(obj, str):
                raise ValueError('Could not find {0}'.format(name))
            if vim_type and not isinstance(obj, vim_type):
                raise ValueError('The given {0}: {1} is not of the correct type'.format(name, attributes[name]))
            return obj
        return False

    def _get_default(self, all_item_in_vc, vim_type, key):
        obj = self._get_default_from_vc_by_type_and_name(all_item_in_vc, vim_type)
        if isinstance(obj, str):
            if obj == 'too many options':
                raise ValueError('{0} must be selected'.format(key))

            raise ValueError('Could not find {0}'.format(key))

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
            raise ValueError('could not connect to the vcenter: {0}, with the given credentials ({1})'.format(
                connection_details.host,
                connection_details.username))
        return si

    def _validate_vm_storage(self, si, all_items_in_vc, auto_att, dc_name, attributes, key):
        accepted_types = (vim.Datastore, vim.StoragePod)
        datastore = self._validate_attribute(si, attributes, accepted_types, key, dc_name)
        if not datastore:
            datastore = self._get_default(all_items_in_vc, accepted_types, key)
            d_name = self.get_full_name(dc_name, datastore)
            # removing the upper folder
            d_name = d_name.replace('datastore/', '')
        else:
            d_name = attributes[key]
        auto_att.append(AutoLoadAttribute('', key, d_name))

    def _validate_vm_location(self, si, all_items_in_vc, auto_att, dc_name, attributes, key):
        accepted_types = None
        folder = self._validate_attribute(si, attributes, accepted_types, key, dc_name)
        if not folder:
            raise ValueError('VM Folder cannot be empty')

        f_name = attributes[key]
        auto_att.append(AutoLoadAttribute('', key, f_name))

    def _validate_vm_cluster(self, si, all_items_in_vc, auto_att, dc_name, attributes, key):
        accepted_types = (vim.ClusterComputeResource, vim.HostSystem)
        cluster = self._validate_attribute(si, attributes, accepted_types, key, dc_name)
        if not cluster:
            cluster = self._get_default(all_items_in_vc, accepted_types, key)
            c_name = self.get_full_name(dc_name, cluster)
            # removing the upper folder
            c_name = c_name.replace('host/', '')
        else:
            c_name = attributes[key]
        auto_att.append(AutoLoadAttribute('', key, c_name))
        return cluster

    def _validate_vm_resource_pool(self, si, all_items_in_vc, auto_att, dc_name, attributes, key):
        cluster = self._validate_vm_cluster(si, all_items_in_vc, auto_att, dc_name, attributes, VM_CLUSTER)

        if key not in attributes or not attributes[key]:
            return
        pool_name = attributes[key]
        pool = self._find_resource_pool_by_path(pool_name, cluster)
        if pool:
            auto_att.append(AutoLoadAttribute('', key, pool_name))
            return

        raise ValueError('The given resource pool not found: {0}'.format(pool_name))

    def _find_resource_pool_by_path(self, name, root):
        paths = name.split('/')
        for path in paths:
            root = self._find_resource_pool(path, root)
            if not root:
                return None
        return root

    def _find_resource_pool(self, name, root):
        if hasattr(root, 'resourcePool'):
            resource_pool = root.resourcePool
            if hasattr(resource_pool, 'name') and resource_pool.name == name:
                return resource_pool

            if isinstance(resource_pool, collections.Iterable):
                for pool in resource_pool:
                    if pool.name == name:
                        return pool

            if hasattr(resource_pool, 'resourcePool'):
                return self._find_resource_pool(name, resource_pool)
        return None

    def _validate_holding_network(self, si, all_items_in_vc, auto_att, dc_name, attributes, key):
        holding_network = self._validate_attribute(si, attributes, vim.Network, key, dc_name)
        if not holding_network:
            raise ValueError('Holding Network cannot be empty')

        n_name = attributes[key]
        auto_att.append(AutoLoadAttribute('', key, n_name))

    def _validate_shutdown_method(self, si, all_items_in_vc, auto_att, dc_name, attributes, key):
        method = attributes[key]
        if self._is_in_array(key, method, SHUTDOWN_METHODS):
            auto_att.append(AutoLoadAttribute('', key, method))

    @staticmethod
    def _is_in_array(key, value, arr):
        if value in arr:
            return True
        raise ValueError('{0} can only be: {1} instead of: {2}'.format(key, arr, value))

    @staticmethod
    def _is_found(item, key):
        if not item:
            raise ValueError('The {0} could not be found in the given vCenter'.format(key))

    @staticmethod
    def _get_connection_details(session, password, user, address):
        password = session.DecryptPassword(password).Value
        return VCenterConnectionDetails(address, user, password)

    @staticmethod
    def _check_if_attribute_not_empty(attributes, name):
        if not ((hasattr(attributes, name) and getattr(attributes, name)) or
                    (isinstance(attributes, dict) and name in attributes and attributes[name])):
            raise ValueError('{0} cannot be empty'.format(name))

    @staticmethod
    def _validate_empty(si, all_items_in_vc, attributes, auto_attr, dc_name, key):
        return

    def _get_validation_method(self, name):
        if not name:
            return self._validate_empty
        name = name.lower()
        name = name.split(' ')
        name = '_'.join(name)
        method_name = '_validate_{0}'.format(name)
        return getattr(self, method_name, self._validate_empty)

    @staticmethod
    def get_full_name(dc_name, managed_object, name=''):
        if managed_object.name == dc_name:
            return name
        curr_path = managed_object.name
        if name:
            curr_path = '{0}/{1}'.format(managed_object.name, name)
        return VCenterAutoModelDiscovery.get_full_name(dc_name, managed_object.parent, curr_path)
