from threading import Lock
from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation


class FolderManager(object):
    def __init__(self, pv_service):
        self.pv_service = pv_service
        self.locks = dict()
        self.locks_lock = Lock()

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
