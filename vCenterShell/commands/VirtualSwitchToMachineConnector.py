from pyVmomi import vim
from pycommon.pyVmomiService import *
from pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter
from vCenterShell.commands.VirtualMachinePortGroupConfigurer import *


class VirtualSwitchToMachineConnector(object):
    def __init__(self, pyvmomi_service, resource_connection_details_retriever, dv_port_group_creator,
                 virtual_machine_port_group_configurer):
        self.pyvmomi_service = pyvmomi_service
        self.resourceConnectionDetailsRetriever = resource_connection_details_retriever
        self.dv_port_group_creator = dv_port_group_creator
        self.virtual_machine_port_group_configurer = virtual_machine_port_group_configurer

    def connect(self, virtual_machine_name, dv_switch_path, dv_switch_name, dv_port_name, virtual_machine_path, vm_uuid,
                port_group_path):
        connection_details = self.resourceConnectionDetailsRetriever.connection_details(virtual_machine_name)

        si = self.pyvmomi_service.connect(connection_details.host, connection_details.username,
                                          connection_details.password,
                                          connection_details.port)

        self.dv_port_group_creator.create_dv_port_group(dv_port_name, dv_switch_name, dv_switch_path, si)

        self.virtual_machine_port_group_configurer.configure_port_group_on_vm(si, virtual_machine_path, vm_uuid,
                                                                              port_group_path,
                                                                              dv_port_name)
