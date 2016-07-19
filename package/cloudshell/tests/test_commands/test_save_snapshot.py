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
