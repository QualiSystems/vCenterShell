from unittest import TestCase
from cloudshell.api.cloudshell_api import VmDetails, ResourceInfo, VmCustomParam
from mock import Mock, create_autospec
from common.logger.service import LoggingService
from common.model_factory import ResourceModelParser
from vCenterShell.commands.refresh_ip import RefreshIpCommand


class TestRefreshIpCommand(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

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

        node = Mock()
        node.attrib = {'Name': 'ip_regex', 'Value': '192\.168\..*'}
        vm_custom_param = VmCustomParam(node, '')

        resource_instance = create_autospec(ResourceInfo)
        resource_instance.ResourceModelName = 'Generic Deployed App'
        resource_instance.ResourceAttributes = {'vm_uuis': '123',
                                                'cloud_provider': 'vCenter'
                                                }
        resource_instance.VmDetails = create_autospec(VmDetails)
        resource_instance.VmDetails.VmCustomParams = [vm_custom_param]

        refresh_ip_command = RefreshIpCommand(pyvmomi_service, ResourceModelParser())
        session = Mock()
        session.UpdateResourceAddress = Mock(return_value=True)
        session.GetResourceDetails = Mock(return_value=resource_instance)
        si = Mock()

        # Act
        refresh_ip_command.refresh_ip(si, session, '1234-5678', 'machine1', 'default_network')

        # Assert
        self.assertTrue(session.UpdateResourceAddress.called_with('machine1', '192.168.1.1'))

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

        node = Mock()
        node.attrib = {'Name': 'ip_regex', 'Value': ''}
        vm_custom_param = VmCustomParam(node, '')

        resource_instance = create_autospec(ResourceInfo)
        resource_instance.ResourceModelName = 'Generic Deployed App'
        resource_instance.ResourceAttributes = {'vm_uuis': '123',
                                                'cloud_provider': 'vCenter'
                                                }
        resource_instance.VmDetails = create_autospec(VmDetails)
        resource_instance.VmDetails.VmCustomParams = [vm_custom_param]

        refresh_ip_command = RefreshIpCommand(pyvmomi_service, ResourceModelParser())
        session = Mock()
        session.UpdateResourceAddress = Mock(return_value=True)
        session.GetResourceDetails = Mock(return_value=resource_instance)
        si = Mock()

        # Act
        refresh_ip_command.refresh_ip(si, session, '1234-5678', 'machine1', 'default_network')

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

        node = Mock()
        node.attrib = {'Name': 'ip_regex', 'Value': '192\.168\..*'}
        vm_custom_param = VmCustomParam(node, '')

        resource_instance = create_autospec(ResourceInfo)
        resource_instance.ResourceModelName = 'Generic Deployed App'
        resource_instance.ResourceAttributes = {'vm_uuis': '123',
                                                'cloud_provider': 'vCenter'
                                                }
        resource_instance.VmDetails = create_autospec(VmDetails)
        resource_instance.VmDetails.VmCustomParams = [vm_custom_param]

        refresh_ip_command = RefreshIpCommand(pyvmomi_service, ResourceModelParser())
        session = Mock()
        session.UpdateResourceAddress = Mock(return_value=True)
        session.GetResourceDetails = Mock(return_value=resource_instance)
        si = Mock()

        # Act
        refresh_ip_command.refresh_ip(si, session, '1234-5678', 'machine1', 'default_network')

        # Assert
        self.assertTrue(session.UpdateResourceAddress.called_with('machine1', '192.168.1.1'))
