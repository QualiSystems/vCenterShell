import time
from pyVmomi import vim

from cloudshell.cp.vcenter.exceptions.user_defined_exceptions import ActionCancelledException


class SynchronousTaskWaiter(object):
    def __init__(self):
        pass

    def _check_cancelation(self, cancellation_context, task, action_name):
        if task.info.cancelable and cancellation_context.is_cancelled and not task.info.cancelled:
            task.CancelTask()
            msg = "Action '{0}' was cancelled.".format(action_name)
            raise ActionCancelledException(msg)

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
        cancellation_context.is_cancelled = True

        while task.info.state in [vim.TaskInfo.State.running, vim.TaskInfo.State.queued]:
            self._check_cancelation(cancellation_context, task, action_name)
            time.sleep(2)

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
