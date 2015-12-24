from pyVmomi import vim
from vCenterShell.pycommon.pyVmomiService import *
from vCenterShell.pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter
from vCenterShell.pycommon.logger import getLogger
logger = getLogger(__name__)


class VirtualMachinePortGroupReConfigurer(object):
    def __init__(self, pyvmomi_service, synchronous_task_waiter):
        self.pyvmomi_service = pyvmomi_service
        self.synchronous_task_waiter = synchronous_task_waiter

    def configure_port_group_on_vm(self, service_instance, virtual_machine_path, vm_uuid, port_group_path,
                                   port_group_name):

        vm = self.pyvmomi_service.find_by_uuid(service_instance, virtual_machine_path, vm_uuid)

        device_change = []
        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard):
                nicspec = vim.vm.device.VirtualDeviceSpec()
                nicspec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                nicspec.device = device
                nicspec.device.wakeOnLanEnabled = True

                network = self.pyvmomi_service.find_network_by_name(service_instance, port_group_path, port_group_name)
                dvs_port_connection = vim.dvs.PortConnection()
                dvs_port_connection.portgroupKey = network.key
                dvs_port_connection.switchUuid = network.config.distributedVirtualSwitch.uuid
                nicspec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
                nicspec.device.backing.port = dvs_port_connection

                nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                nicspec.device.connectable.startConnected = True
                nicspec.device.connectable.allowGuestControl = True
                device_change.append(nicspec)
                break

        config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
        task = vm.ReconfigVM_Task(config_spec)
        logger.info("Successfully changed network")
        return self.synchronous_task_waiter.wait_for_task(task)
