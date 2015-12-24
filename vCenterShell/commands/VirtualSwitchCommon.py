# -*- coding: utf-8 -*-

"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info
"""

from pyVmomi import vim
from vCenterShell.pycommon.pyVmomiService import *

from vCenterShell.commands.BaseCommand import BaseCommand
from vCenterShell.pycommon.utilites.lazy_property import lazy_property
frompycommon.logger import getLogger

_logger = getLogger("vCenterShell")

#@todo only for development purposes - can be removed in next
from vCenterShell.models.VCenterConnectionDetails import VCenterConnectionDetails
from vCenterShell.pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from vCenterShell.pycommon.pyVmomiService import pyVmomiService
from vCenterShell.commands.DvPortGroupCreator import DvPortGroupCreator
from vCenterShell.commands.VirtualMachinePortGroupConfigurer import VirtualMachinePortGroupConfigurer


#@todo move to more suitable place
def connection_detaiuls_by_vm_name(vm_name, connection_retriever):
    assert (issubclass(type(connection_retriever), ResourceConnectionDetailsRetriever))
    connection_details = connection_retriever.connection_details(vm_name)

    if not connection_details:
        _logger.warn(u"Cannot get connection info based on '{}'".format(vm_name))
    return connection_details


#@todo move to more suitable place
def service_connection(connection_details, pyvmomi_service, connection_retriever):
    """
    Connect to vCenter via SSL and return 'Service Instance' (SI) object
    :param vm_name: <str> Name of Virtual Machine
    :param pyvmomi_service: <pyVmomiService>
    :param connection_retriever: <ResourceConnectionDetailsRetriever>
    :return: <obj> 'service instance' (si)
    """

    #@todo only for development purposes - can be removed in next
    assert (issubclass(type(connection_retriever), ResourceConnectionDetailsRetriever))
    assert (issubclass(type(pyvmomi_service), pyVmomiService))
    assert(isinstance(connection_details, VCenterConnectionDetails))

    _logger.debug("Connection to vCenter  Via [{host}:{port}] User: '{username}'".format(
        **connection_details.as_dict()))

    service_instance = pyvmomi_service.connect( connection_details.host,
                                                connection_details.username,
                                                connection_details.password,
                                                connection_details.port)

    _logger.debug("Connection created {}".format("SUCCESS" if service_instance else "UN SUCCESS"))
    return service_instance


class VirtualSwitchCommandBase(BaseCommand):
    """
    Abstract Base Switch Class
    """
    def __init__(self,
                 connection_details,
                 pyvmomi_service,
                 connection_retriever,
                 port_group_creator,
                 port_group_configurator):

        #@todo only for development purposes - can be removed in next
        assert (issubclass(type(connection_details), VCenterConnectionDetails))
        assert (issubclass(type(pyvmomi_service), pyVmomiService))
        assert (issubclass(type(connection_retriever), ResourceConnectionDetailsRetriever))
        assert (issubclass(type(port_group_creator), DvPortGroupCreator))
        assert (isinstance(port_group_configurator, VirtualMachinePortGroupConfigurer))

        self.connection_details = connection_details
        self.pyvmomi_service = pyvmomi_service
        self.connection_retriever = connection_retriever
        self.port_group_creator = port_group_creator
        self.port_group_configurator = port_group_configurator


    @lazy_property
    def si(self):
        """
        :return: 'Service Instance' (SI) object
        """
        return service_connection(self.connection_details,
                                  self.pyvmomi_service,
                                  self.connection_retriever)



    # def get_virtual_machine(self, service_instance, vm_path, vm_uuid):
    #     vm = self.pyvmomi_service.find_by_uuid(service_instance, vm_path, vm_uuid)
