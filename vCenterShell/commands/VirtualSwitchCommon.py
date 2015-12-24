# -*- coding: utf-8 -*-

"""
@see https://waffle.io/QualiSystems/vCenterShell/cards/5666b2aa0c076d2300052216 for initial info
"""

from pyVmomi import vim
from pycommon.pyVmomiService import *

from vCenterShell.commands.BaseCommand import BaseCommand
from pycommon.utilites.lazy_property import lazy_property
from pycommon.logger import getLogger

_logger = getLogger("vCenterShell")

#@todo only for development purposes - can be removed in next
from models.VCenterConnectionDetails import VCenterConnectionDetails
from pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever
from pycommon.pyVmomiService import pyVmomiService
from pycommon.SynchronousTaskWaiter import SynchronousTaskWaiter


#@todo move to more suitable place
def connection_details_by_vm_name(vm_name, connection_retriever):
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
                 pyvmomi_service,
                 connection_retriever,
                 synchronous_task_waiter=None):

        #@todo only for development purposes - can be removed in next
        assert (issubclass(type(pyvmomi_service), pyVmomiService))
        assert (issubclass(type(connection_retriever), ResourceConnectionDetailsRetriever))


        self.pyvmomi_service = pyvmomi_service
        self.connection_retriever = connection_retriever
        self.synchronous_task_waiter = synchronous_task_waiter

        self._service_instance = None

    def is_vcenter_connected(self):
        return bool(self._service_instance)

    def vcenter_connect(self, connection_details):
        self._service_instance = service_connection(connection_details, self.pyvmomi_service, self.connection_retriever)

    @property
    def si(self):
        return self.service_instance()

    def service_instance(self):
        return self._service_instance

    def get_connection_details(self, vm_name):
        return connection_details_by_vm_name(vm_name, self.connection_retriever)

    def get_virtual_machine(self, service_instance, vm_path, vm_uuid):
        vm = self.pyvmomi_service.find_by_uuid(service_instance, vm_path, vm_uuid)
