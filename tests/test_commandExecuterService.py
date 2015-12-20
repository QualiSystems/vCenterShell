import unittest
from mock import MagicMock, Mock
from vCenterShell.commands.CommandExecuterService import CommandExecuterService


class TestCommandExecuterService(unittest.TestCase):
    def test_connect_execute_was_called(self):
        # Arrange
        network_adapter_retriever_command = MagicMock()
        command_executer_service = CommandExecuterService(None, network_adapter_retriever_command, Mock(), Mock())

        # Act
        command_executer_service.connect()

        # Assert
        network_adapter_retriever_command.execute.assert_called_with()
