from unittest import TestCase
from mock import Mock
from uuid import uuid4 as guid

from cloudshell.cp.vcenter.commands.save_app import SaveAppCommand
from cloudshell.cp.core.models import SaveApp, SaveAppParams


class TestSaveAppCommand(TestCase):
    def setUp(self):
        self.save_command = SaveAppCommand(Mock(), Mock())

    def test_save_app_command_fails_when_missing_save_app_actions(self):
        with self.assertRaises(Exception) as context:
            self._save_app_without_actions()
        self.assertIn('Failed to save app, missing data in request.', context.exception.message)

    def test_save_app_command(self):
        save_action = self._create_arbitrary_save_app_action()

        result = self.save_command.save_app(si=Mock(),
                                            logger=Mock(),
                                            save_app_actions=[save_action],
                                            cancellation_context=None)

        # Assert
        self.assertTrue(result.type == 'saveApp')

    def _save_app_without_actions(self):
        self.save_command.save_app(si=Mock(),
                                   logger=Mock(),
                                   save_app_actions=[],
                                   cancellation_context=None)

    def _create_arbitrary_save_app_action(self):
        save_action = SaveApp()
        actionParams = SaveAppParams()
        actionParams.savedType = 'linked_clone'
        actionParams.savedSandboxId = guid()
        actionParams.sourceVmUuid = guid()
        save_action.actionParams = actionParams
        return save_action
