from unittest import TestCase
from mock import Mock, MagicMock
from common.logger.service import LoggingService
from vCenterShell.commands.refresh_ip import RefreshIpCommand


class TestRefreshIpCommand(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def test_refresh_ip(self):
        nic = Mock()
        nic.network = 'A Network'
        nic.ipAddress = ['192.168.1.1']

        guest = Mock()
        guest.net = [nic]

        vm = Mock()
        vm.guest = guest

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        refresh_ip_command = RefreshIpCommand(pyvmomi_service)
        session = Mock()
        session.UpdateResourceAddress = Mock(return_value=True)
        si = Mock()

        # Act
        refresh_ip_command.refresh_ip(session, si, '1234-5678', 'machine1', 'default_network')

        # Assert
        self.assertTrue(session.UpdateResourceAddress.called_with('machine1', '192.168.1.1'))

