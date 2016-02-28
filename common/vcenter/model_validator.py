from pyVim.connect import SmartConnect, Disconnect

from pyVmomi import vim
from common.cloud_shell.driver_helper import CloudshellDriverHelper
from common.model_factory import ResourceModelParser
from common.vcenter.vmomi_service import pyVmomiService
from models.VMwarevCenterResourceModel import VMwarevCenterResourceModel


class VCenterModelValidator(object):
    def __init__(self):
        self.parser = ResourceModelParser()
        self.pv_service = pyVmomiService(SmartConnect, Disconnect)
        self.cs_helper = CloudshellDriverHelper()

    def validate(self, context):
        """
        :type context: models.QualiDriverModels.AutoLoadCommandContext
        """
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             None)

        self._check_if_attribute_not_empty(context.resource.address, 'Address')

        vcenter_model = self.parser.convert_to_resource_model(context.resource, VMwarevCenterResourceModel)
        """:type : models.VMwarevCenterResourceModel.VMwarevCenterResourceModel"""

        si = self._check_if_vcenter_user_pass_valid(context, session, vcenter_model)

        self._validate_dvswitch_or_set_default(si, vcenter_model)
        self._validate_holding_network(si, vcenter_model)
        self._validate_default_port_group(si, vcenter_model)
        self._validate_cluster_or_set_default(si, vcenter_model)
        self._validate_resource_pool(si, vcenter_model)
        self._validate_storage_or_set_default(si, vcenter_model)
        self._check_if_attrib_exists(si, vcenter_model.vm_location, 'VM Location')
        self._validate_or_set_default('shut_down_method', vcenter_model, ['hard', 'soft'], 'Shut Down Method')
        self._check_if_bool(vcenter_model.promiscuous_mode, 'Promiscuous Mode')

    def _validate_dvswitch_or_set_default(self, si, vcenter_model):
        if vcenter_model.default_dvswitch:
            self._validate_attr(si, vcenter_model.default_dvswitch, 'Default DvSwitch')
        else:
            default = self.pv_service.get_default_from_vcenter_by_type(self, si, vim.Cluster, False)
            vcenter_model.default_dvswitch = '{0}/{1}'.format(default.parent.name, default.name)

    def _validate_holding_network(self, si, vcenter_model):
        self._check_if_attribute_not_empty(vcenter_model.holding_network, 'Holding Network')

        default = self.pv_service.get_default_from_vcenter_by_type(si, vim.Datastore, True)
        self._validate_attr(default, default, 'Holding Network')

    def _validate_default_port_group(self, si, vcenter_model):
        if vcenter_model.default_port_group_location:
            self._validate_attr(si,
                                '{0}/{1}'.format(vcenter_model.default_dvswitch,
                                                 vcenter_model.default_port_group_location),
                                'Default Port Group Location')

    def _validate_cluster_or_set_default(self, si, vcenter_model):
        if vcenter_model.vm_cluster:
            self._validate_attr(si, vcenter_model.vm_cluster, 'VM Cluster')
        else:
            default = self.pv_service.get_default_from_vcenter_by_type(self, si, vim.Cluster, False)
            vcenter_model.vm_cluster = '{0}/{1}'.format(default.parent.name, default.name)

    def _validate_resource_pool(self, si, vcenter_model):
        if not vcenter_model.vm_resource_pool:
            return
        self._check_if_key_in_vcenter(si, vcenter_model.vm_cluster + '/' + vcenter_model.vm_resource_pool,
                                      'VM Resource Pool')

    def _validate_storage_or_set_default(self, si, vcenter_model):
        if vcenter_model.vm_storage:
            self._validate_attr(si, vcenter_model.vm_storage, 'VM Storage')
        else:
            default = self.pv_service.get_default_from_vcenter_by_type(self, si, vim.Datastore, False)
            vcenter_model.vm_storage = '{0}/{1}'.format(default.parent.name, default.name)

    def _validate_attr(self, si, attr, msg):
        a = self.pv_service.find_obj_by_path(si, attr, msg)
        self._check_if_resource_found(a, msg, attr)

    def _check_if_attrib_exists(self, si, attrib, msg):
        self._check_if_attribute_not_empty(attrib, msg)
        self._check_if_key_in_vcenter(si, attrib, msg)

    def _check_if_key_in_vcenter(self, si, attrib, msg):
        resource = self.pv_service.get_folder(si, attrib)
        self._check_if_resource_found(attrib, msg, resource)

    @staticmethod
    def _check_if_resource_found(attrib, msg, resource):
        if resource:
            raise KeyError('could not found: {0} at path: {1}'.format(msg, attrib))

    def _validate_or_set_default(self, name, model, accepet_values, msg):
        attribute = getattr(model, name)
        if not isinstance(accepet_values, list):
            accepet_values = [accepet_values]
        if attribute:
            self._check_if_in_restricted_values(attribute, msg, accepet_values)
        else:
            setattr(model, name, accepet_values[0])

    def _check_if_vcenter_user_pass_valid(self, context, session, vcenter_model):
        self._check_if_attribute_not_empty(vcenter_model.user, 'User')
        self._check_if_attribute_not_empty(vcenter_model.password, 'Password')
        connection_details = self.cs_helper.get_connection_details(session, vcenter_model, context.resource)
        si = self.pv_service.connect(connection_details.host,
                                     connection_details.username,
                                     connection_details.password,
                                     connection_details.port)
        if not si:
            raise KeyError('could not connect to the vcenter: {0}, with the given credentials ({1})'.format(
                connection_details.host,
                connection_details.username))
        return si

    @staticmethod
    def _check_if_in_restricted_values(attribute, name, values):
        VCenterModelValidator._check_if_attribute_not_empty(attribute, name)
        if not VCenterModelValidator._check_if_in(attribute, values):
            raise KeyError('{0} value: {1}, but must be of {2}'.format(name, attribute, values))

    @staticmethod
    def _check_if_bool(attribute, name):
        VCenterModelValidator._check_if_attribute_not_empty(attribute, name)
        if not (VCenterModelValidator._check_if_in(attribute, [True, 'True', 'true']) or
                VCenterModelValidator._check_if_in(attribute, [False, 'False', 'false'])):
            raise KeyError('{0} must be a boolean instead of {1}'.format(name, attribute))

    @staticmethod
    def _check_if_in(attribute, arr):
        return attribute in arr

    @staticmethod
    def _check_if_attribute_not_empty(attribute, name):
        if not attribute:
            raise KeyError('{0} cannot be empty'.format(name))
