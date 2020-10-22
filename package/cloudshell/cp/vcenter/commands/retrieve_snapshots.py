from cloudshell.cp.vcenter.common.vcenter.vm_snapshots import SnapshotRetriever
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService


class RetrieveSnapshotsCommand:
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
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)
        logger.info("Get snapshots")
        snapshots = SnapshotRetriever.get_vm_snapshots(vm)

        return list(snapshots.keys())
