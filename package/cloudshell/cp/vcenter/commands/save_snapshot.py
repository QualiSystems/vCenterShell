from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vm_snapshots import SnapshotRetriever
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.exceptions.snapshot_exists import SnapshotAlreadyExistsException

SNAPSHOT_ALREADY_EXISTS = 'A snapshot of this name already exist under this VM. Please select a different name for the VM snapshot'


class SaveSnapshotCommand:
    def __init__(self, pyvmomi_service, task_waiter):
        """
        Creates an instance of SnapshotSaver
        :param pyvmomi_service:
        :type pyvmomi_service: pyVmomiService
        :param task_waiter: Waits for the task to be completed
        :type task_waiter:  SynchronousTaskWaiter
        :return:
        """
        self.pyvmomi_service = pyvmomi_service
        self.task_waiter = task_waiter

    def save_snapshot(self, si, logger, vm_uuid, snapshot_name):
        """
        Creates a snapshot of the current state of the virtual machine

        :param vim.ServiceInstance si: py_vmomi service instance
        :type si: vim.ServiceInstance
        :param logger: Logger
        :type logger: cloudshell.core.logger.qs_logger.get_qs_logger
        :param vm_uuid: UUID of the virtual machine
        :type vm_uuid: str
        :param snapshot_name: Snapshot name to save the snapshot to
        :type snapshot_name: str
        """
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)

        snapshot_path_to_be_created = SaveSnapshotCommand._get_snapshot_name_to_be_created(snapshot_name, vm)
        SaveSnapshotCommand._verify_snapshot_uniquness(snapshot_path_to_be_created, vm)

        task = self._create_snapshot(logger, snapshot_name, vm)

        self.task_waiter.wait_for_task(task=task, logger=logger, action_name='Create Snapshot')
        return snapshot_path_to_be_created

    @staticmethod
    def _create_snapshot(logger, snapshot_name, vm):
        logger.info("Create virtual machine snapshot")
        dump_memory = False
        quiesce = True
        task = vm.CreateSnapshot(snapshot_name, 'Created by CloudShell vCenterShell', dump_memory, quiesce)
        return task

    @staticmethod
    def _verify_snapshot_uniquness(snapshot_path_to_be_created, vm):
        all_snapshots = SnapshotRetriever.get_vm_snapshots(vm)
        if snapshot_path_to_be_created in all_snapshots:
            raise SnapshotAlreadyExistsException(SNAPSHOT_ALREADY_EXISTS)

    @staticmethod
    def _get_snapshot_name_to_be_created(snapshot_name, vm):
        current_snapshot_name = SnapshotRetriever.get_current_snapshot_name(vm)
        if not current_snapshot_name:
            return ''
        return SnapshotRetriever.combine(current_snapshot_name, snapshot_name)
