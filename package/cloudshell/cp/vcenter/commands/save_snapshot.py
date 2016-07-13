from pyVmomi import vim
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser
from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter


class SnapshotSaver:
    def __init__(self, pyvmomi_service, resource_model_parser, task_waiter):
        """
        Creates an instance of SnapshotSaver
        :param pyvmomi_service:
        :type pyvmomi_service: pyVmomiService
        :param resource_model_parser: Converts to flat resource model
        :type resource_model_parser: ResourceModelParser
        :param task_waiter: Waits for the task to be completed
        :type task_waiter:  SynchronousTaskWaiter
        :return:
        """
        self.pyvmomi_service = pyvmomi_service
        self.resource_model_parser = resource_model_parser
        self.task_waiter = task_waiter

    def save_snapshot(self, si, logger, vcenter_data_model, snapshot_name):
        """
        Refreshes IP address of virtual machine and updates Address property on the resource

        :param vim.ServiceInstance si: py_vmomi service instance
        :param logger: Logger
        :param str snapshot_name: Snapshot name to save the snapshot to
        :param VMwarevCenterResourceModel vcenter_data_model: the vcenter data model attributes
        """
        vm = self.pyvmomi_service.find_by_uuid(si, vcenter_data_model.vm_uuid)
        logger.info("Create virtual machine snapshot")

        try:
            dump_memory = False
            quiesce = True
            task = vm.CreateSnapshot(snapshot_name, 'Created by CloudShell vCenterShell', dump_memory, quiesce)

            return self.task_waiter.wait_for_task(task=task, logger=logger, action_name='Create Snapshot')

        except vim.fault.NoPermission as error:
            logger.error("vcenter returned - no permission: {0}".format(error))
            raise Exception('Permissions is not set correctly, please check the log for more info.')
        except Exception as e:
            logger.error("error deploying: {0}".format(e))
            raise Exception('Error has occurred while creating snapshot, please look at the log for more info.')

