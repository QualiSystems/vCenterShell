from unittest import TestCase

from cloudshell.api.cloudshell_api import VmDetails, ResourceInfo, VmCustomParam
from mock import Mock, create_autospec
from cloudshell.cp.vcenter.commands.refresh_ip import RefreshIpCommand
from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser


class TestRefreshIpCommand(TestCase):

    def test_refresh_ip(self):
        nic1 = Mock()
        nic1.network = 'A Network'
        nic1.ipAddress = ['192.168.1.1']

        nic2 = Mock()
        nic2.network = 'A Network'
        nic2.ipAddress = ['111.111.111.111']

        guest = Mock()
        guest.toolsStatus = 'toolsOk'
        guest.net = [nic1, nic2]

        vm = Mock()
        vm.guest = guest

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        ip_regex = self._create_custom_param('ip_regex', '192\.168\..*')
        refresh_ip_timeout = self._create_custom_param('refresh_ip_timeout', '10')

        resource_instance = create_autospec(ResourceInfo)
        resource_instance.ResourceModelName = 'Generic Deployed App'
        resource_instance.ResourceAttributes = {'vm_uuis': '123',
                                                'cloud_provider': 'vCenter'
                                                }
        resource_instance.VmDetails = create_autospec(VmDetails)
        resource_instance.VmDetails.VmCustomParams = [ip_regex, refresh_ip_timeout]

        refresh_ip_command = RefreshIpCommand(pyvmomi_service, ResourceModelParser())
        session = Mock()
        session.UpdateResourceAddress = Mock(return_value=True)
        session.GetResourceDetails = Mock(return_value=resource_instance)
        si = Mock()

        center_resource_model = VMwarevCenterResourceModel()
        center_resource_model.default_datacenter = 'QualiSB'
        center_resource_model.holding_network = 'anetwork'
        cancellation_context = Mock()

        # Act
        refresh_ip_command.refresh_ip(si=si,
                                      session=session,
                                      vcenter_data_model= center_resource_model,
                                      vm_uuid='machine1',
                                      resource_name='default_network',
                                      cancellation_context=cancellation_context,
                                      logger=Mock())

        # Assert
        self.assertTrue(session.UpdateResourceAddress.called_with('machine1', '192.168.1.1'))

    def _create_custom_param(self, name, value):
        node = Mock()
        node.attrib = {'Name': name, 'Value': value}
        vm_custom_param = VmCustomParam(node, '')
        vm_custom_param.Name = name
        vm_custom_param.Value = value
        return vm_custom_param

    def test_refresh_ip_choose_ipv4(self):
        nic1 = Mock()
        nic1.network = 'A Network'
        nic1.ipAddress = ['192.168.1.1']

        nic2 = Mock()
        nic2.network = 'A Network'
        nic2.ipAddress = ['2001:0db8:0a0b:12f0:0000:0000:0000:0001']

        guest = Mock()
        guest.toolsStatus = 'toolsOk'
        guest.net = [nic1, nic2]

        vm = Mock()
        vm.guest = guest

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        ip_regex = self._create_custom_param('ip_regex', '')
        refresh_ip_timeout = self._create_custom_param('refresh_ip_timeout', '10')

        resource_instance = create_autospec(ResourceInfo)
        resource_instance.ResourceModelName = 'Generic Deployed App'
        resource_instance.ResourceAttributes = {'vm_uuis': '123',
                                                'cloud_provider': 'vCenter'
                                                }
        resource_instance.VmDetails = create_autospec(VmDetails)
        resource_instance.VmDetails.VmCustomParams = [ip_regex, refresh_ip_timeout]

        refresh_ip_command = RefreshIpCommand(pyvmomi_service, ResourceModelParser())
        session = Mock()
        session.UpdateResourceAddress = Mock(return_value=True)
        session.GetResourceDetails = Mock(return_value=resource_instance)
        si = Mock()

        center_resource_model = VMwarevCenterResourceModel()
        center_resource_model.default_datacenter = 'QualiSB'
        center_resource_model.holding_network = 'anetwork'
        cancellation_context = Mock()

        # Act
        refresh_ip_command.refresh_ip(
            si=si,
            session=session,
            vcenter_data_model=center_resource_model,
            vm_uuid='machine1',
            resource_name='default_network',
            cancellation_context=cancellation_context,
            logger=Mock())

        # Assert
        self.assertTrue(session.UpdateResourceAddress.called_with('machine1', '192.168.1.1'))

    def test_refresh_ip_choose_ip_by_regex(self):
        nic1 = Mock()
        nic1.network = 'A Network'
        nic1.ipAddress = ['192.168.1.1']

        nic2 = Mock()
        nic2.network = 'A Network'
        nic2.ipAddress = ['111.111.111.111']

        guest = Mock()
        guest.toolsStatus = 'toolsOk'
        guest.net = [nic1, nic2]

        vm = Mock()
        vm.guest = guest

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        ip_regex = self._create_custom_param('ip_regex', '192\.168\..*')
        refresh_ip_timeout = self._create_custom_param('refresh_ip_timeout', '10')

        resource_instance = create_autospec(ResourceInfo)
        resource_instance.ResourceModelName = 'Generic Deployed App'
        resource_instance.ResourceAttributes = {'vm_uuis': '123',
                                                'cloud_provider': 'vCenter'
                                                }
        resource_instance.VmDetails = create_autospec(VmDetails)
        resource_instance.VmDetails.VmCustomParams = [ip_regex, refresh_ip_timeout]

        refresh_ip_command = RefreshIpCommand(pyvmomi_service, ResourceModelParser())
        session = Mock()
        session.UpdateResourceAddress = Mock(return_value=True)
        session.GetResourceDetails = Mock(return_value=resource_instance)
        si = Mock()

        center_resource_model = VMwarevCenterResourceModel()
        center_resource_model.default_datacenter = 'QualiSB'
        center_resource_model.holding_network = 'anetwork'
        cancellation_context = Mock()

        # Act
        refresh_ip_command.refresh_ip(
            si=si,
            session=session,
            vcenter_data_model=center_resource_model,
            vm_uuid='machine1',
            resource_name='default_network',
            cancellation_context=cancellation_context,
            logger=Mock())

        # Assert
        self.assertTrue(session.UpdateResourceAddress.called_with('machine1', '192.168.1.1'))
