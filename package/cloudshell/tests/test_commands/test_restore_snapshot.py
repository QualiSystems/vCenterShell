from unittest import TestCase

from mock import Mock, patch

from cloudshell.cp.vcenter.commands.restore_snapshot import SnapshotRestoreCommand
from cloudshell.cp.vcenter.exceptions.snapshot_not_found import SnapshotNotFoundException


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
        self.assertRaises(SnapshotNotFoundException, snapshot_restore_command.restore_snapshot, si, Mock(), 'machine1',
                          'NOT_EXISTING_SNAPSHOT')
