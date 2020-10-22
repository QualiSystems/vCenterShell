import collections

from pyVmomi import vim


class SnapshotRetriever:
    def __init__(self):
        pass

    @staticmethod
    def get_current_snapshot_name(vm):
        """
        Returns the name of the current snapshot
        :param vm: Virtual machine to find current snapshot name
        :return: Snapshot name
        :rtype str
        """
        all_snapshots = SnapshotRetriever.get_vm_snapshots(vm)
        # noinspection PyProtectedMember
        if not vm.snapshot:
            return None
        current_snapshot_id = vm.snapshot.currentSnapshot._moId
        for snapshot_name in list(all_snapshots.keys()):
            # noinspection PyProtectedMember
            if all_snapshots[snapshot_name]._moId == current_snapshot_id:
                return snapshot_name
        return None

    @staticmethod
    def get_vm_snapshots(vm):
        """
        Returns dictinary of snapshots of a given virtual machine
        Key is full path to snapshot, for example RootSnapshot/ChildSnapshot/LeadSnapshot
        Value is an instance of snapshot
        :param vm: an instance of virtual machine
        :type vim.vm.VirtualMachine
        :return:
        """
        if not vm.snapshot:
            return {}
        return SnapshotRetriever._get_snapshots_recursively(vm.snapshot.rootSnapshotList, '')

    @staticmethod
    def _get_snapshots_recursively(snapshots, snapshot_location):
        """
        Recursively traverses child snapshots and returns dictinary of snapshots
        :param snapshots: list of snapshots to examine
        :param snapshot_location: current path of snapshots
        :return: dictinary of snapshot path and snapshot instances
        :rtype: dict(str,vim.vm.Snapshot)
        """
        snapshot_paths = collections.OrderedDict()

        if not snapshots:
            return snapshot_paths

        for snapshot in snapshots:
            if snapshot_location:
                current_snapshot_path = SnapshotRetriever.combine(snapshot_location, snapshot.name)
            else:
                current_snapshot_path = snapshot.name

            snapshot_paths[current_snapshot_path] = snapshot.snapshot
            child_snapshots = SnapshotRetriever._get_snapshots_recursively(snapshot.childSnapshotList,
                                                                           current_snapshot_path)
            snapshot_paths.update(child_snapshots)

        return snapshot_paths

    @staticmethod
    def combine(base_snapshot_location, snapshot_name):
        """
        Combines snapshot path
        :param base_snapshot_location:
        :param snapshot_name:
        :return: combined snapshot path
        :rtype str
        """
        return base_snapshot_location + '/' + snapshot_name
