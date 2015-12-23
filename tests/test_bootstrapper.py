from unittest import TestCase
from vCenterShell.pycommon import Bootstrapper
from vCenterShell import Bootstrapper


class TestBootstrapper(TestCase):
    def test_get_command_executer_service(self):
        # Arrange
        bootstrapper = Bootstrapper.Bootstrapper()

        # Act
        command_executer_service = bootstrapper.get_command_executer_service()

        # Assert
        self.assertIsNotNone(command_executer_service)
