import unittest
from mock import MagicMock, Mock
from vCenterShell.commands.CommandExecuterService import CommandExecuterService


class TestCommandExecuterService(unittest.TestCase):
    def test_destroyVirtualMachineCommand(self):
        destroy_virtual_machine_command = MagicMock()
        command_executer_service = CommandExecuterService(None, None, destroy_virtual_machine_command, None)

        command_executer_service.destroy()

        destroy_virtual_machine_command.execute.assert_called_with()
