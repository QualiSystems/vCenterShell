from pyVmomi import vim

from cloudshell.cp.vcenter.common.vcenter.vm_snapshots import SnapshotRetriever
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter


class SnapshotRestoreCommand:
    def __init__(self, pyvmomi_service, task_waiter):
        """
        Creates an instance of SnapshotRestorer
        :param pyvmomi_service:
        :type pyvmomi_service: pyVmomiService
        :param task_waiter: Waits for the task to be completed
        :type task_waiter:  SynchronousTaskWaiter
        :return:
        """
        self.pyvmomi_service = pyvmomi_service
        self.task_waiter = task_waiter

    def restore_snapshot(self, si, logger, vm_uuid, snapshot_name):
        """
        Restores a virtual machine to a snapshot
        :param vim.ServiceInstance si: py_vmomi service instance
        :param logger: Logger
        :param vm_uuid: uuid of the virtual machine
        :param str snapshot_name: Snapshot name to save the snapshot to
        """
        try:

            vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)
            logger.info("Revert snapshot")

            snapshot = SnapshotRestoreCommand._get_snapshot(vm=vm, snapshot_name=snapshot_name)
            task = snapshot.RevertToSnapshot_Task()
            return self.task_waiter.wait_for_task(task=task, logger=logger, action_name='Revert Snapshot')

        except vim.fault.NoPermission as error:
            logger.error("vcenter returned - no permission: {0}".format(error))
            raise Exception('Permissions is not set correctly, please check the log for more info.')
        except Exception as e:
            logger.error("error reverting to snapshot: {0}".format(e))
            raise Exception('Error has occurred while reverting to snapshot, please look at the log for more info.')

    @staticmethod
    def _get_snapshot(vm, snapshot_name):
        """
        Returns snapshot object by its name
        :param vm:
        :param snapshot_name:
        :type snapshot_name: str
        :return: Snapshot by its name
        :rtype vim.vm.Snapshot
        """
        snapshots = SnapshotRetriever.get_vm_snapshots(vm)

        if snapshot_name not in snapshots:
            raise Exception('Snapshot {0} was not found'.format(snapshot_name))

        return snapshots[snapshot_name]

