# -*- coding: utf-8 -*-
"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info
"""

from pyVmomi import vim
from vCenterShell.pycommon.pyVmomiService import *
from vCenterShell.pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter
from vCenterShell.commands.VirtualMachinePortGroupConfigurer import *
from vCenterShell.models.VCenterConnectionDetails import VCenterConnectionDetails

import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim

from vCenterShell.commands.BaseCommand import BaseCommand

from vCenterShell.pycommon.logger import getLogger

_logger = getLogger("vCenterShell")


def vm_connection(vm_name, connection_retriever):
    connection_details = connection_retriever.connection_details(vm_name)

    if not connection_details:
        _logger.warn("Cannot get connection info for connect to VM '{}'".format(vm_name))
        return None

    assert(isinstance(connection_details, VCenterConnectionDetails))

    _logger.debug("Connection to VM '{}' Via [{host}:{port}] User: '{username}'".format(
        vm_name, **connection_details.as_dict()))

    # _logger.debug("Connection to VM '{}' Via [{}:{}] User: '{}'".format(
    #     vm_name, connection_details.host, connection_details.port, connection_details.username))
    pass


class VirtualSwitchToMachineDisConnector(BaseCommand):
    def __init__(self, pyvmomi_service, resource_connection_details_retriever, dv_port_group_creator,
                 virtual_machine_port_group_configurer):
        self.pyvmomi_service = pyvmomi_service
        self.resourceConnectionDetailsRetriever = resource_connection_details_retriever
        self.dv_port_group_creator = dv_port_group_creator
        self.virtual_machine_port_group_configurer = virtual_machine_port_group_configurer

    def disconnect(self, virtual_machine_name, dv_switch_path, dv_switch_name, dv_port_name, virtual_machine_path, vm_uuid,
                port_group_path):

        connection_details = self.resourceConnectionDetailsRetriever.connection_details(virtual_machine_name)

        si = self.pyvmomi_service.connect(connection_details.host, connection_details.username,
                                          connection_details.password,
                                          connection_details.port)

        self.dv_port_group_creator.create_dv_port_group(dv_port_name, dv_switch_name, dv_switch_path, si)

        self.virtual_machine_port_group_configurer.configure_port_group_on_vm(si, virtual_machine_path, vm_uuid,
                                                                              port_group_path,
                                                                              dv_port_name)


    def execute(self):
        pass