import time
from pyVmomi import vim

from cloudshell.cp.vcenter.exceptions.invalid_host_state_exception import InvalidHostStateException


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

            if type(task.info.error) is vim.fault.InvalidHostState:
                err_msg = task.info.error.Message + ' ' + task.info.error.msg
                msg_n_err_msg = "vim.fault.InvalidHostState:" + multi_msg + '\n' + err_msg
                logger.info(msg_n_err_msg)
                raise InvalidHostStateException(msg_n_err_msg)

            logger.info(multi_msg)
            raise Exception(multi_msg)

        return task.info.result
