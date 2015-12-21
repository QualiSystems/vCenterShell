from pyVmomi import vim
import uuid
from vCenterShell.pycommon.pyVmomiService import *
from vCenterShell.pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter


class VirtualSwitchToMachineConnector(object):
    def __init__(self, pyvmomi_service, resource_connection_details_retriever, dv_port_group_creator,
                 synchronous_task_waiter):
        self.pyvmomi_service = pyvmomi_service
        self.resourceConnectionDetailsRetriever = resource_connection_details_retriever
        self.dv_port_group_creator = dv_port_group_creator
        self.synchronous_task_waiter = synchronous_task_waiter

    def connect(self, virtual_machine_name, dv_switch_path, dv_switch_name, dv_port_name, virtual_machine_path, vm_uuid,
                network_name):

        connection_details = self.resourceConnectionDetailsRetriever.connection_details(virtual_machine_name)

        si = self.pyvmomi_service.connect(connection_details.host, connection_details.username,
                                          connection_details.password,
                                          connection_details.port)

        port_group = self.dv_port_group_creator.create_dv_port_group(dv_port_name, dv_switch_name, dv_switch_path, si)

        connection = self.connect_vm_to_port_group(si, virtual_machine_path, vm_uuid, dv_port_name,
                                                   virtual_machine_name, True)

        return connection

    def connect_vm_to_port_group(self, service_instance, virtual_machine_path, vm_uuid, network_name,
                                 virtual_machine_name, is_vds):

        # atexit.register(connect.Disconnect, service_instance)
        content = service_instance.RetrieveContent()
        vm = self.pyvmomi_service.find_by_uuid(service_instance, virtual_machine_path, vm_uuid)
        # vm = self.pyvmomi_service.find_vm_by_name(service_instance, virtual_machine_path, virtual_machine_name)
        # This code is for changing only one Interface. For multiple Interface
        # Iterate through a loop of network names.
        device_change = []
        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard):
                nicspec = vim.vm.device.VirtualDeviceSpec()
                nicspec.operation = \
                    vim.vm.device.VirtualDeviceSpec.Operation.edit
                nicspec.device = device
                nicspec.device.wakeOnLanEnabled = True

                if not is_vds:
                    nicspec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                    nicspec.device.backing.network = self.pyvmomi_service.get_obj(content, [vim.Network], network_name)
                    nicspec.device.backing.deviceName = network_name
                else:
                    network = self.pyvmomi_service.get_obj(content, [vim.dvs.DistributedVirtualPortgroup], network_name)
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
        print "Successfully changed network"
        return self.synchronous_task_waiter.wait_for_task(service_instance, [task])
