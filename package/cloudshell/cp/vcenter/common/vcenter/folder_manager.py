from threading import Lock
from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation


class FolderManager(object):
    def __init__(self, pv_service, task_waiter):
        self.pv_service = pv_service
        self.locks = dict()
        self.locks_lock = Lock()
        self.task_waiter = task_waiter

    def delete_folder(self, si, logger, folder_full_path):
        logger.info('Trying to remove {0} and all child folders and vms'.format(folder_full_path))
        folder = self.pv_service.get_folder(si, folder_full_path)

        if not folder:
            logger.info('Could not find {0}, maybe it was already removed?'.format(folder_full_path))

        vms, _ = self.pv_service.get_folder_contents(folder, True)

        for vm in vms:
            self.pv_service.power_off_before_destroy(logger, vm)

        if folder_full_path not in self.locks.keys():
            with self.locks_lock:
                if folder_full_path not in self.locks.keys():
                    self.locks[folder_full_path] = Lock()

        with self.locks[folder_full_path]:
            task = folder.Destroy_Task()
            result = self.task_waiter.wait_for_task(task=task, logger=logger, action_name="Destroy Folder")

        logger.info('Remove result for {0} and all child folders and vms\n{1}'.format(folder_full_path, result))

    def get_or_create_vcenter_folder(self, si, logger, path, folder_name):
        logger.info('Getting or creating {0} in {1}'.format(folder_name, path))
        folder_parent = self.pv_service.get_folder(si, path)
        if not folder_parent:
            logger.error('Could not find {0}'.format(path))
            raise Exception("Could not find " + path)

        vcenter_folder_path = VMLocation.combine([path, folder_name])

        if vcenter_folder_path not in self.locks.keys():
            with self.locks_lock:
                if vcenter_folder_path not in self.locks.keys():
                    self.locks[vcenter_folder_path] = Lock()

        vcenter_folder = self.pv_service.get_folder(si, vcenter_folder_path)
        if not vcenter_folder:
            with self.locks[vcenter_folder_path]:
                vcenter_folder = self.pv_service.get_folder(si, vcenter_folder_path)
                if not vcenter_folder:
                    logger.info('{0} was not found under {1}, creating...'.format(folder_name, path))
                    folder_parent.CreateFolder(folder_name)
                    logger.info('{0} created in path {1}'.format(folder_name, path))
                else:
                    logger.info('{0} already exists'.format(folder_name))

        return vcenter_folder
