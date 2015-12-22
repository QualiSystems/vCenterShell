import time
from pyVmomi import vim, vmodl


class SynchronousTaskWaiter(object):
    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def wait_for_task(self, task, actionName='job', hideResult=False):
        """
        Waits and provides updates on a vSphere task
        :param hideResult:
        :param actionName:
        :param task:
        """

        while task.info.state == vim.TaskInfo.State.running:
            time.sleep(2)

        if task.info.state == vim.TaskInfo.State.success:
            if task.info.result is not None and not hideResult:
                out = '%s completed successfully, result: %s' % (actionName, task.info.result)
                print out
            else:
                out = '%s completed successfully.' % actionName
                print out
        else:
            out = '%s did not complete successfully: %s' % (actionName, task.info.error)
            print out
            raise task.info.error

        return task.info.result
