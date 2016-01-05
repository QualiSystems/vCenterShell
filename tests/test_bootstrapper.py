from unittest import TestCase

from common.logger.service import LoggingService
from vCenterShell import bootstrap


class TestBootstrapper(TestCase):
    LoggingService("CRITICAL", "DEBUG", None)

    def test_get_command_executer_service(self):
        # Arrange
        bootstrapper = bootstrap.Bootstrapper()

        # Act
        command_executer_service = bootstrapper.get_command_executer_service()

        # Assert
        self.assertIsNotNone(command_executer_service)
