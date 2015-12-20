import unittest
from mock import MagicMock
from vCenterShell.commands.CommandExecuterService import CommandExecuterService


class TestCommandExecuterService(unittest.TestCase):
    def test_connect_execute_was_called(self):
        # Arrange
        virtual_switch_connect_command = MagicMock()
        command_executer_service = CommandExecuterService(None, None, virtual_switch_connect_command)

        # Act
        command_executer_service.connect()

        # Assert
        virtual_switch_connect_command.execute.assert_called_with()
