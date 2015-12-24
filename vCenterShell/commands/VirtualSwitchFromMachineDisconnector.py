# -*- coding: utf-8 -*-
"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info
"""

from pyVmomi import vim
from vCenterShell.pycommon.pyVmomiService import *
from vCenterShell.pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter
from vCenterShell.commands.VirtualMachinePortGroupConfigurer import *


import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim

#from vCenterShell.commands.BaseCommand import BaseCommand

from .VirtualSwitchCommon import VirtualSwitchCommandBase

frompycommon.logger import getLogger

_logger = getLogger("vCenterShell")


#@todo move to more suitable place
def vm_connection(vm_name, pyvmomi_service, connection_retriever):
    """
    Get Service Instance based on a Virtual Machine Name
    :param vm_name: <str> Name of Virtual Machine
    :param pyvmomi_service: <pyVmomiService>
    :param connection_retriever: <ResourceConnectionDetailsRetriever>
    :return: <obj> 'service instance' (si)
    """

    from vCenterShell.models.VCenterConnectionDetails import VCenterConnectionDetails
    from vCenterShell.pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
    from vCenterShell.pycommon.pyVmomiService import pyVmomiService

    assert (issubclass(type(connection_retriever), ResourceConnectionDetailsRetriever))
    assert (issubclass(type(pyvmomi_service), pyVmomiService))

    connection_details = connection_retriever.connection_details(vm_name)

    if not connection_details:
        _logger.warn("Cannot get connection info for connect to VM '{}'".format(vm_name))
        return None

    assert(isinstance(connection_details, VCenterConnectionDetails))

    _logger.debug("Connection to VM '{}' Via [{host}:{port}] User: '{username}'".format(
        vm_name, **connection_details.as_dict()))

    si = pyvmomi_service.connect(connection_details.host,
                                 connection_details.username,
                                 connection_details.password,
                                 connection_details.port)

    _logger.debug("Connection created {}".format("SUCCESS" if si else "UN SUCCESS"))

    return si



class VirtualSwitchFromMachineDisconnector(VirtualSwitchCommandBase):

    def __init__(self,
                 pyvmomi_service,
                 connection_retriever,
                 port_group_creator,
                 port_group_configurator):
        super(VirtualSwitchFromMachineDisconnector, self).__init__(
            pyvmomi_service, connection_retriever, port_group_creator, port_group_configurator)


    def disconnect(self, vm_name, switch_path, switch_name, port_name, vm_path, vm_uuid, port_group_path):
        si = self.get_connection(vm_name)


        self.dv_port_group_creator.create_dv_port_group(dv_port_name, dv_switch_name, dv_switch_path, si)

        self.virtual_machine_port_group_configurer.configure_port_group_on_vm(si, virtual_machine_path, vm_uuid,
                                                                              port_group_path,
                                                                              dv_port_name)


    def execute(self):
        pass