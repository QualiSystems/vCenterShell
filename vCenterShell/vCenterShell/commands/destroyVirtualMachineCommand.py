from pyVmomi import vim
import requests
import atexit
from qualipy.api.cloudshell_api import *
import qualipy.scripts.cloudshell_scripts_helpers as helpers
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers
import time
import sys
import vCenterShell.pycommon
from vCenterShell.pycommon.common_name_utils import generate_unique_name
from vCenterShell.pycommon.CloudshellDataRetrieverService import *


class DestroyVirtualMachineCommand(object):
    """ Command to Destroy a VM """

    def __init__(self, pvService):
        """
        :param pvService:   pyVmomiService Instance
        """
        self.pvService = pvService
        self.csRetrieverService = CloudshellDataRetrieverService()

    def execute(self):
        """ execute the command """

        resource_att = helpers.get_resource_context_details()

        # get vCenter resource name
        inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_att)
        vCenter_resource_name = inventory_path_data["vCenter_resource_name"]
        vm_folder = inventory_path_data["vm_folder"]

        print "Folder: {0}, vCenter: {1}".format(vm_folder, vCenter_resource_name)

        reservation_id = helpers.get_reservation_context_details().id
        session = helpers.get_api_session()
        vCenter_details = session.GetResourceDetails(vCenter_resource_name)

        # get vCenter connection details from vCenter resource
        vCenterConn = self.csRetrieverService.getVCenterConnectionDetails(session, vCenter_details)

        print "Connecting to: {0}, As: {1}, Pwd: {2}".format(vCenterConn["vCenter_url"], vCenterConn["user"],
                                                             vCenterConn["password"])

        # connect
        si = self.pvService.connect(vCenterConn["vCenter_url"], vCenterConn["user"], vCenterConn["password"])
        content = si.RetrieveContent()

        # destroy the vm
        vm_name = resource_att.name
        self.pvService.destroy_vm_by_name(si, vm_name)

        # disconnect
        self.pvService.disconnect(si)

        # delete resource 
        helpers.get_api_session() \
            .DeleteResource(resource_att.fullname)
