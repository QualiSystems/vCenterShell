class SnapshotRetriever:
    def __init__(self):
        pass

    @staticmethod
    def get_vm_snapshots(vm):
        if not vm.snapshot:
            return {}
        return SnapshotRetriever._get_snapshots_recursively(vm.snapshot.rootSnapshotList, '')

    @staticmethod
    def _get_snapshots_recursively(snapshots, snapshot_location):
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
