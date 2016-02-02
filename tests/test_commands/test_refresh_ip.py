from unittest import TestCase
from mock import Mock, MagicMock
from common.logger.service import LoggingService
from vCenterShell.commands.refresh_ip import RefreshIpCommand


class TestRefreshIpCommand(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def test_refresh_ip(self):

        resource_model_parser = Mock()

        qualipy_helpers = MagicMock()

        session = MagicMock()

        qualipy_helpers.get_api_session = Mock(return_value=session)

        nic = Mock()
        nic.network = 'A Network'
        nic.ipAddress = ['192.168.1.1']

        guest = Mock()
        guest.net = [nic]

        vm = Mock()
        vm.guest = guest

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        refresh_ip_command = RefreshIpCommand(pyvmomi_service, Mock(), qualipy_helpers, resource_model_parser)

        si = Mock()

        # Act
        refresh_ip_command.refresh_ip(si, '1234-5678', 'machine1')

        # Assert
        session.UpdateResourceAddress.assert_called_with('machine1', '192.168.1.1')

    def test_refresh_ip_choose_ipv4(self):

        resource_model_parser = Mock()

        qualipy_helpers = MagicMock()

        session = MagicMock()

        qualipy_helpers.get_api_session = Mock(return_value=session)

        nic_ip_v4 = Mock()
        nic_ip_v4.network = 'A Network'
        nic_ip_v4.ipAddress = ['192.168.1.1']

        nic_ip_v6 = Mock()
        nic_ip_v6.network = 'Dark Network'
        nic_ip_v6.ipAddress = ['00-01-00-01-1B-BE-E5-51-44-8A-5B-BF-AC-4E']

        guest = Mock()
        guest.net = [nic_ip_v6, nic_ip_v4]

        vm = Mock()
        vm.guest = guest

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        refresh_ip_command = RefreshIpCommand(pyvmomi_service, Mock(), qualipy_helpers, resource_model_parser)

        si = Mock()

        # Act
        refresh_ip_command.refresh_ip(si, '1234-5678', 'machine1')

        # Assert
        session.UpdateResourceAddress.assert_called_with('machine1', '192.168.1.1')

