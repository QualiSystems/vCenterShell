from pyVmomi import vim
from unittest import TestCase

from mock import Mock

from cloudshell.cp.vcenter.commands.save_snapshot import SaveSnapshotCommand


class TestSaveSnapshotCommand(TestCase):
    def test_save_snapshot_succeeds(self):
        vm = Mock()

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        save_snapshot_command = SaveSnapshotCommand(pyvmomi_service, Mock())
        si = Mock()

        # Act
        save_snapshot_command.save_snapshot(si=si,
                                            logger=Mock(),
                                            vm_uuid='machine1',
                                            snapshot_name='new_snapshot')

        # Assert
        vm.CreateSnapshot.called_with('new_snapshot', 'Created by CloudShell vCenterShell', False, True)

    def test_exception_raised_when_save_snapshot_fails_with_no_permission_exception(self):
        vm = Mock()
        vm.CreateSnapshot = Mock(side_effect=vim.fault.NoPermission())
        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        save_snapshot_command = SaveSnapshotCommand(pyvmomi_service, Mock())
        si = Mock()
        logger = Mock()

        # Act + Assert
        self.assertRaises(Exception, save_snapshot_command.save_snapshot, si, logger, 'machine1', 'new_snapshot')
        logger.error.assert_called()

    def test_exception_raised_when_save_snapshot_fails_with_general_exception(self):
        vm = Mock()
        vm.CreateSnapshot = Mock(side_effect=Exception())
        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        save_snapshot_command = SaveSnapshotCommand(pyvmomi_service, Mock())
        si = Mock()
        logger = Mock()

        # Act + Assert
        self.assertRaises(Exception, save_snapshot_command.save_snapshot, si, logger, 'machine1', 'new_snapshot')
        logger.error.assert_called()
