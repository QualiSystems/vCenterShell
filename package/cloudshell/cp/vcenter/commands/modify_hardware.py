from cloudshell.cp.vcenter.common.vcenter.task_waiter import SynchronousTaskWaiter
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.api.cloudshell_api import CloudShellAPISession
import json
from pyVmomi import vim


class ModifyHardwareCommand:
    def __init__(self, pyvmomi_service, task_waiter, resource_model_parser):
        """
        Creates an instance of HardwareModifier
        :param pyvmomi_service:
        :type pyvmomi_service: pyVmomiService
        :param task_waiter: Waits for the task to be completed
        :type task_waiter:  SynchronousTaskWaiter
        :return:
        """
        self.pyvmomi_service = pyvmomi_service
        self.task_waiter = task_waiter
        self.resource_model_parser = resource_model_parser

    def modify_vm_hardware(self, si, logger, session, vcenter_data_model, vm_uuid, vm_changes):
        """
        Restores a virtual machine to a snapshot
        :param vim.ServiceInstance si: py_vmomi service instance
        :param logger: Logger
        :param session: CloudShellAPISession
        :type session: cloudshell_api.CloudShellAPISession
        :param vm_uuid: uuid of the virtual machine
        :param resource_fullname:
        :type: resource_fullname: str
        :param str snapshot_name: Snapshot name to save the snapshot to
        """
        hardware_changes = json.loads(vm_changes)
        cspec = vim.vm.ConfigSpec()
        content = si.RetrieveContent()
        vm = self.pyvmomi_service.find_by_uuid(si, vm_uuid)
        if 'cpu' in hardware_changes:
            cspec.numCPUs = hardware_changes['cpu']
        if 'memory' in hardware_changes:
            cspec.memoryMB = hardware_changes['memory'] * 1024  # origin in gbs
        if 'nics' in hardware_changes:
            for nic in range(hardware_changes['nics']):
                cspec.deviceChange.append(self._add_nic(content, vcenter_data_model.holding_network,
                                                        vcenter_data_model.default_dvswitch))

        logger.info("Modifying vm hardware")

        task = vm.Reconfigure(cspec)
        return self.task_waiter.wait_for_task(task=task, logger=logger, action_name='Revert Snapshot')

    @staticmethod
    def _add_nic(content, network, dvswitch):
        """
        Prepare a device config spec for a new virtual NIC (for reconfig_vm())
        """
        nic_spec = vim.vm.device.VirtualDeviceSpec()
        nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add

        nic_spec.device = vim.vm.device.VirtualVmxnet3()

        nic_spec.device.deviceInfo = vim.Description()
        nic_spec.device.deviceInfo.summary = network

        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        pg = _get_obj(content, [vim.Network], network)
        dvs_port_connection = vim.dvs.PortConnection()
        dvs_port_connection.portgroupKey = pg.key
        dvs_port_connection.switchUuid = pg.config.distributedVirtualSwitch.uuid
        nic_spec.device.backing.port = dvs_port_connection

        nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic_spec.device.connectable.startConnected = True
        nic_spec.device.connectable.startConnected = True
        nic_spec.device.connectable.allowGuestControl = True
        nic_spec.device.connectable.connected = True
        nic_spec.device.connectable.status = 'untried'

        nic_spec.device.wakeOnLanEnabled = True
        nic_spec.device.addressType = 'assigned'

        return nic_spec


def _get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj
