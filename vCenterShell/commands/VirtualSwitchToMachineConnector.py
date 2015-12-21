from pyVmomi import vim
import uuid
from vCenterShell.pycommon.pyVmomiService import *


class VirtualSwitchToMachineConnector(object):
    def __init__(self, pyvmomi_service, resource_connection_details_retriever, dv_port_group_creator):
        self.pyvmomi_service = pyvmomi_service
        self.resourceConnectionDetailsRetriever = resource_connection_details_retriever
        self.dv_port_group_creator = dv_port_group_creator

    def connect(self, virtual_machine_name, dv_switch_path, dv_switch_name, dv_port_name):
        connection_details = self.resourceConnectionDetailsRetriever.connection_details(virtual_machine_name)
        si = self.pyvmomi_service.connect(connection_details.host, connection_details.username,
                                          connection_details.password,
                                          connection_details.port)

        port_group = self.dv_port_group_creator.create_dv_port_group(dv_port_name, dv_switch_name, dv_switch_path, si)

        return port_group


