from unittest import TestCase

from mock import Mock, patch
from pyVmomi import vim

from cloudshell.cp.vcenter.commands.retrieve_snapshots import RetrieveSnapshotsCommand


class TestRetrieveSnapshotCommand(TestCase):
    @patch('cloudshell.cp.vcenter.commands.restore_snapshot.SnapshotRetriever.get_vm_snapshots')
    def test_restore_snapshot_should_success_on_existing_snapshot(self, mock_get_vm_snapshots):
        vm = Mock()

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        snapshot_restore_command = RetrieveSnapshotsCommand(pyvmomi_service=pyvmomi_service)
        si = Mock()

        mock_get_vm_snapshots.return_value = {'snap1': Mock()}

        # Act
        snapshots = snapshot_restore_command.get_snapshots(si=si, logger=Mock(), vm_uuid='machine1')

        # Assert
        self.assertSequenceEqual(snapshots, ['snap1'])

    def test_exception_raised_when_get_snapshots_fails_with_no_permission_exception(self):
        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(side_effect=vim.fault.NoPermission())

        retrieve_snapshot_command = RetrieveSnapshotsCommand(pyvmomi_service)
        si = Mock()
        logger = Mock()

        # Act + Assert
        self.assertRaises(Exception, retrieve_snapshot_command.get_snapshots, si, logger, 'machine1')
        logger.error.assert_called()

    def test_exception_raised_when_save_snapshot_fails_with_general_exception(self):
        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(side_effect=Exception())

        retrieve_snapshot_command = RetrieveSnapshotsCommand(pyvmomi_service)
        si = Mock()
        logger = Mock()

        # Act + Assert
        self.assertRaises(Exception, retrieve_snapshot_command.get_snapshots, si, logger, 'machine1')
        logger.error.assert_called()
