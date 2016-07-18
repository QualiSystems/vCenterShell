from pyVmomi import vim
from unittest import TestCase
from mock import Mock, patch
from cloudshell.cp.vcenter.commands.restore_snapshot import SnapshotRestoreCommand


class TestSnapshotRestoreCommand(TestCase):
    @patch('cloudshell.cp.vcenter.commands.restore_snapshot.SnapshotRetriever.get_vm_snapshots')
    def test_restore_snapshot_should_success_on_existing_snapshot(self, mock_get_vm_snapshots):
        vm = Mock()

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        snapshot_restore_command = SnapshotRestoreCommand(pyvmomi_service=pyvmomi_service,
                                                          task_waiter=Mock())
        si = Mock()

        snapshot = Mock()
        mock_get_vm_snapshots.return_value = {'snap1': snapshot}

        # Act
        snapshot_restore_command.restore_snapshot(si=si,
                                                  logger=Mock(),
                                                  vm_uuid='machine1',
                                                  snapshot_name='snap1')

        # Assert
        self.assertTrue(snapshot.RevertToSnapshot_Task.called)

    @patch('cloudshell.cp.vcenter.commands.restore_snapshot.SnapshotRetriever.get_vm_snapshots')
    def test_restore_snapshot_should_throw_exception_on_none_existing_snapshot(self, mock_get_vm_snapshots):
        vm = Mock()

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        snapshot_restore_command = SnapshotRestoreCommand(pyvmomi_service=pyvmomi_service,
                                                          task_waiter=Mock())
        si = Mock()

        mock_get_vm_snapshots.return_value = {'snap1': Mock()}

        # Act + Assert
        self.assertRaises(Exception, snapshot_restore_command.restore_snapshot, si, Mock(), 'machine1',
                          'NOT_EXISTING_SNAPSHOT')

    def test_exception_raised_when_restore_snapshot_fails_with_no_permission_exception(self):
        vm = Mock()
        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        with patch('cloudshell.cp.vcenter.commands.restore_snapshot.SnapshotRetriever.get_vm_snapshots') as get_vm_snapshots:
            snapshot = Mock()
            snapshot.RevertToSnapshot_Task = Mock(side_effect=vim.fault.NoPermission())
            get_vm_snapshots.return_value = {'new_snapshot': snapshot}
            snapshot_restore_command = SnapshotRestoreCommand(pyvmomi_service, Mock())
            si = Mock()
            logger = Mock()

            # Act + Assert
            self.assertRaises(Exception, snapshot_restore_command.restore_snapshot, si, logger, 'machine1', 'new_snapshot')
            logger.error.assert_called()

    def test_exception_raised_when_restore_snapshot_fails_with_general_exception(self):
        vm = Mock()
        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        with patch('cloudshell.cp.vcenter.commands.restore_snapshot.SnapshotRetriever.get_vm_snapshots') as get_vm_snapshots:
            snapshot = Mock()
            snapshot.RevertToSnapshot_Task = Mock(side_effect=Exception())
            get_vm_snapshots.return_value = {'new_snapshot': snapshot}
            snapshot_restore_command = SnapshotRestoreCommand(pyvmomi_service, Mock())
            si = Mock()
            logger = Mock()

            # Act + Assert
            self.assertRaises(Exception, snapshot_restore_command.restore_snapshot, si, logger, 'machine1', 'new_snapshot')
            logger.error.assert_called()
