import time, os
from pyVmomi import vim, vmodl
from common.logger import getLogger
from common.logger import configure_loglevel
logger = getLogger(__name__)
# configure_loglevel("INFO", "INFO", os.path.join(__file__, os.pardir, os.pardir, os.pardir, 'logs', 'vCenter.log'))

class SynchronousTaskWaiter(object):
    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def wait_for_task(self, task, action_name='job', hideResult=False):
        """
        Waits and provides updates on a vSphere task
        :param hideResult:
        :param action_name:
        :param task:
        """

        while task.info.state == vim.TaskInfo.State.running:
            time.sleep(2)

        if task.info.state == vim.TaskInfo.State.success:
            if task.info.result is not None and not hideResult:
                out = '%s completed successfully, result: %s' % (action_name, task.info.result)
                logger.info(out)
            else:
                out = '%s completed successfully.' % action_name
                logger.info(out)
        else:
            out = '%s did not complete successfully: %s' % (action_name, task.info.error)
            logger.info(out)
            raise task.info.error

        return task.info.result
