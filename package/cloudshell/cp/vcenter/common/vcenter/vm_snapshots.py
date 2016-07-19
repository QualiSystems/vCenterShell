from pyVmomi import vim


class SnapshotRetriever:
    def __init__(self):
        pass

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
        :rtype: dict
        """
        snapshot_paths = {}

        if not snapshots:
            return snapshot_paths

        for snapshot in snapshots:
            if snapshot_location:
                current_snapshot_path = snapshot_location + '/' + snapshot.name
            else:
                current_snapshot_path = snapshot.name

            snapshot_paths[current_snapshot_path] = snapshot.snapshot
            child_snapshots = SnapshotRetriever._get_snapshots_recursively(snapshot.childSnapshotList,
                                                                           current_snapshot_path)
            snapshot_paths.update(child_snapshots)

        return snapshot_paths
