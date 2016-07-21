import unittest

from mock import Mock

from cloudshell.cp.vcenter.common.vcenter.vm_snapshots import SnapshotRetriever


class TestSnapshotRetriever(unittest.TestCase):
    def test_ctor(self):
        snapshot_retriever = SnapshotRetriever()
        self.assertIsNotNone(snapshot_retriever)

    def test_empty_dict_when_vm_has_no_snapshots(self):
        # Arrange
        vm = Mock()
        vm.snapshot = None

        # Act
        all_snapshots = SnapshotRetriever.get_vm_snapshots(vm)

        # assert
        self.assertSequenceEqual(all_snapshots, {})

    def test_one_snapshot_when_one_snapshot_exists(self):
        # Arrange
        snapshot = Mock()
        snapshot.name = 'snap1'
        snapshot.childSnapshotList = []

        vm = Mock()
        vm.snapshot = Mock()
        vm.snapshot.rootSnapshotList = [snapshot]

        # Act
        all_snapshots = SnapshotRetriever.get_vm_snapshots(vm)

        # assert
        self.assertSequenceEqual(all_snapshots.keys(), ['snap1'])

    def test_two_snapshots_when_root_snapshot_has_a_child(self):
        # Arrange
        child = Mock()
        child.name = 'child'
        child.childSnapshotList = []

        root = Mock()
        root.name = 'root'
        root.childSnapshotList = [child]

        vm = Mock()
        vm.snapshot = Mock()
        vm.snapshot.rootSnapshotList = [root]

        # Act
        all_snapshots = SnapshotRetriever.get_vm_snapshots(vm)

        # assert
        self.assertSequenceEqual(all_snapshots.keys(), ['root', 'root/child'])

    def test_combine_should_combine_base_snapshot_location_with_snapshot_name(self):
        # Act
        snapshot_path = SnapshotRetriever.combine('snapshot1/snapshot2', 'snapshot3')

        # Assert
        self.assertEqual(snapshot_path, 'snapshot1/snapshot2/snapshot3')

    def test_cet_current_snapshot_returns_none_when_no_snapshot_exists(self):
        # Arrange
        vm = Mock()
        vm.snapshot = None

        # Act
        current_snapshot_name = SnapshotRetriever.get_current_snapshot_name(vm)

        # assert
        self.assertIsNone(current_snapshot_name)
