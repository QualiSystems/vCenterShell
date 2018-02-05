from unittest import TestCase

from mock import Mock, patch

from cloudshell.cp.vcenter.commands.save_snapshot import SaveSnapshotCommand
from cloudshell.cp.vcenter.exceptions.snapshot_exists import SnapshotAlreadyExistsException

GET_VM_SNAPSHOTS = 'cloudshell.cp.vcenter.commands.save_snapshot.SnapshotRetriever.get_vm_snapshots'

GET_CURRENT_SNAPSHOT_NAME = 'cloudshell.cp.vcenter.commands.save_snapshot.SnapshotRetriever.get_current_snapshot_name'


class TestSaveSnapshotCommand(TestCase):
    def test_save_snapshot_should_succeed_when_there_is_no_snapshot(self):
        vm = Mock()

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        save_snapshot_command = SaveSnapshotCommand(pyvmomi_service, Mock())
        si = Mock()

        # Act
        with patch(GET_CURRENT_SNAPSHOT_NAME) as get_current_snapshot_name:
            with patch(GET_VM_SNAPSHOTS) as get_vm_snapshots:
                get_current_snapshot_name.return_value = None
                get_vm_snapshots.return_value = {}
                save_snapshot_command.save_snapshot(si=si,
                                                    logger=Mock(),
                                                    vm_uuid='machine1',
                                                    snapshot_name='new_snapshot',
                                                    save_memory='No')

        # Assert
        vm.CreateSnapshot.called_with('new_snapshot', 'Created by CloudShell vCenterShell', False, True)

    def test_save_snapshot_should_succeed_when_snapshot_with_the_same_name_does_not_exists(self):
        vm = Mock()

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        save_snapshot_command = SaveSnapshotCommand(pyvmomi_service, Mock())
        si = Mock()

        # Act
        with patch(GET_CURRENT_SNAPSHOT_NAME) as get_current_snapshot_name:
            with patch(GET_VM_SNAPSHOTS) as get_vm_snapshots:
                get_current_snapshot_name.return_value = 'snapshot1/snapshot2'
                get_vm_snapshots.return_value = {'snapshot1/snapshot2': None, 'snapshot1': None}
                save_snapshot_command.save_snapshot(si=si,
                                                    logger=Mock(),
                                                    vm_uuid='machine1',
                                                    snapshot_name='new_snapshot',
                                                    save_memory='No')

        # Assert
        vm.CreateSnapshot.called_with('new_snapshot', 'Created by CloudShell vCenterShell', False, True)

    def test_save_snapshot_should_fail_if_snaphost_exists(self):
        vm = Mock()

        pyvmomi_service = Mock()
        pyvmomi_service.find_by_uuid = Mock(return_value=vm)

        save_snapshot_command = SaveSnapshotCommand(pyvmomi_service, Mock())
        si = Mock()

        with patch(GET_CURRENT_SNAPSHOT_NAME) as get_current_snapshot_name:
            with patch(GET_VM_SNAPSHOTS) as get_vm_snapshots:
                    get_current_snapshot_name.return_value = 'snapshot1'
                    get_vm_snapshots.return_value = {'snapshot1': None, 'snapshot1/snapshot2': None}

                    # Act + Assert
                    with self.assertRaises(SnapshotAlreadyExistsException):
                        save_snapshot_command.save_snapshot(si=si,
                                                            logger=Mock(),
                                                            vm_uuid='machine1',
                                                            snapshot_name='snapshot2',
                                                            save_memory='No')

    def test_save_memory_yes(self):
        save_memory_string = 'Yes'
        self.assertTrue(SaveSnapshotCommand._get_save_vm_memory_to_snapshot(save_memory_string))
        save_memory_string = 'yEs'
        self.assertTrue(SaveSnapshotCommand._get_save_vm_memory_to_snapshot(save_memory_string))

    def test_save_memory_no(self):
        save_memory_string = 'No'
        self.assertTrue(not SaveSnapshotCommand._get_save_vm_memory_to_snapshot(save_memory_string))
        save_memory_string = 'nO'
        self.assertTrue(not SaveSnapshotCommand._get_save_vm_memory_to_snapshot(save_memory_string))