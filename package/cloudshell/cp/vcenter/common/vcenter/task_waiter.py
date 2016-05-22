import time
from pyVmomi import vim


class SynchronousTaskWaiter(object):
    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def wait_for_task(self, task, logger, action_name='job', hide_result=False):
        """
        Waits and provides updates on a vSphere task
        :param task:
        :param action_name:
        :param hide_result:
        :param logger:
        """

        while task.info.state in [vim.TaskInfo.State.running, vim.TaskInfo.State.queued]:
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
            raise Exception(multi_msg)

        return task.info.result
