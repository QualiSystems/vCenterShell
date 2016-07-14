from pyVmomi import vim
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService


class SnapshotRetriever:
    def __init__(self, pyvmomi_service):
        """
        Creates an instance of SnapshotRestorer
        :param pyvmomi_service:
        :type pyvmomi_service: pyVmomiService
        :return:
        """
        self.pyvmomi_service = pyvmomi_service

    def get_snapshots(self, si, logger, vm_uuid):
        """
        Restores a virtual machine to a snapshot
        :param vim.ServiceInstance si: py_vmomi service instance
        :param logger: Logger
        :param vm_uuid: uuid of the virtual machine
        """
        try:
            vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)
            logger.info("Get snapshots")

            snapshots = vm.snapshot.rootSnapshotList
            return [snapshot.name for snapshot in snapshots]

        except vim.fault.NoPermission as error:
            logger.error("vcenter returned - no permission: {0}".format(error))
            raise Exception('Permissions is not set correctly, please check the log for more info.')
        except Exception as e:
            logger.error("error reverting to snapshot: {0}".format(e))
            raise Exception('Error has occurred while reverting to snapshot, please look at the log for more info.')

