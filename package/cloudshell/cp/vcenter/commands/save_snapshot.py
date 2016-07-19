from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService


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
        logger.info("Create virtual machine snapshot")

        dump_memory = False
        quiesce = True
        task = vm.CreateSnapshot(snapshot_name, 'Created by CloudShell vCenterShell', dump_memory, quiesce)

        return self.task_waiter.wait_for_task(task=task, logger=logger, action_name='Create Snapshot')
