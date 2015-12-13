from pyVmomi import vim
import requests
import atexit
from qualipy.api.cloudshell_api import *
import qualipy.scripts.cloudshell_scripts_helpers as helpers
import time
import sys
import pycommon
from pycommon.common_name_utils import generate_unique_name
from pycommon.cloudshellDataRetrieverService import *
from commands.baseCommand import BaseCommand

class deployFromTemplateCommand(BaseCommand):
    """ Command to Create a VM from a template """


    def __init__(self, pvService):
        """
        :param pvService:   pyVmomiService Instance
        """
        self.pvService = pvService
        self.csRetrieverService = cloudshellDataRetrieverService()


    def execute(self):    
        """ execute the command """

        resource_att = helpers.get_resource_context_details()        

        # get vCenter resource name, template name, template folder
        vCenterTemplateAttData = self.csRetrieverService.getVCenterTemplateAttributeData(resource_att)
        template_name = vCenterTemplateAttData["template_name"]
        vCenter_resource_name = vCenterTemplateAttData["vCenter_resource_name"]
        vm_folder = vCenterTemplateAttData["vm_folder"]

        print "Template: {0}, Folder: {1}, vCenter: {2}".format(template_name, vm_folder, vCenter_resource_name)
    

        # get power state of the cloned VM
        power_on = self.csRetrieverService.getPowerStateAttributeData(resource_att)

        print "Power On: {0}".format(power_on)


        # get cluster and resource pool
        vmClusterAttData = self.csRetrieverService.getVMClusterAttributeData(resource_att)
        cluster_name = vmClusterAttData["cluster_name"]
        resource_pool = vmClusterAttData["resource_pool"]

        print "Cluster: {0}, Resource Pool: {1}".format(cluster_name, resource_pool)


        # get datastore
        datastore_name = self.csRetrieverService.getVMStorageAttributeData(resource_att)

        print "Datastore: {0}".format(datastore_name)


        reservation_id = helpers.get_reservation_context_details().id
        session = helpers.get_api_session()
        vCenter_details = session.GetResourceDetails(vCenter_resource_name)
    
        # get vCenter connection details from vCenter resource
        vCenterConn = self.csRetrieverService.getVCenterConnectionDetails(session, vCenter_details)

        print "Connecting to: {0}, As: {1}, Pwd: {2}".format(vCenterConn["vCenter_url"] , vCenterConn["user"], vCenterConn["password"])
 
        # connect
        si = self.pvService.connect(vCenterConn["vCenter_url"] , vCenterConn["user"], vCenterConn["password"])
        content = si.RetrieveContent()

        template = self.pvService.get_obj(content, [vim.VirtualMachine], template_name)
    
        if template:
            # generate unique name
            vm_name = generate_unique_name(template_name)

            vm = self.pvService.clone_vm(
                content = content, 
                si = si,
                template = template, 
                vm_name = vm_name,
                datacenter_name = None, 
                vm_folder = vm_folder, 
                datastore_name = datastore_name, 
                cluster_name = cluster_name,
                resource_pool = resource_pool,
                power_on = power_on)

            helpers.get_api_session() \
                .CreateResource("Virtual Machine",
                                "Virtual Machine", 
                                vm_name,
                                vm_name)
            helpers.get_api_session() \
                .AddResourcesToReservation(reservation_id, [vm_name])
            helpers.get_api_session() \
                .SetAttributesValues(
                    [ResourceAttributesUpdateRequest(vm_name, 
                        [AttributeNameValue("vCenter Inventory Path", vCenter_resource_name + "/" + vm_folder),
                        AttributeNameValue("UUID", vm.summary.config.instanceUuid),
                        AttributeNameValue("vCenter Template", resource_att.attributes["vCenter Template"])])])

        else:
            print "template not found"

        # disconnect
        self.pvService.disconnect(si)


    
        
        

  



