import time
from pyVmomi import vim


class SynchronousTaskWaiter(object):
    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def wait_for_task(self, task, logger, action_name='job', hide_result=False, cancellation_context=None):
        """
        Waits and provides updates on a vSphere task
        :param cancellation_context: package.cloudshell.cp.vcenter.models.QualiDriverModels.CancellationContext
        :param task: https://github.com/vmware/pyvmomi/blob/master/docs/vim/Task.rst
        :param action_name:
        :param hide_result:
        :param logger:
        """

        while task.info.state in [vim.TaskInfo.State.running, vim.TaskInfo.State.queued]:
            time.sleep(2)
            if cancellation_context is not None and task.info.cancelable and cancellation_context.is_cancelled and not task.info.cancelled:
                # some times the cancel operation doesn't really cancel the task
                # so consider an additional handling of the canceling
                task.CancelTask()
                logger.info("SynchronousTaskWaiter: task.CancelTask() " + str(task.info.name.info.name))
                logger.info("SynchronousTaskWaiter: task.info.cancelled " + str(task.info.cancelled))
                logger.info("SynchronousTaskWaiter: task.info.state " + str(task.info.state))

        if task.info.state == vim.TaskInfo.State.success:
            if task.info.result is not None and not hide_result:
                out = '%s completed successfully, result: %s' % (action_name, task.info.result)
                logger.info(out)
            else:
                out = '%s completed successfully.' % action_name
                logger.info(out)
        else:  # error state
            multi_msg = ''
            if task.info.error.faultMessage:
                multi_msg = ', '.join([err.message for err in task.info.error.faultMessage])

            logger.info(multi_msg)
            logger.info("task info dump: {0}".format(task.info))

            raise Exception(multi_msg)

        return task.info.result
