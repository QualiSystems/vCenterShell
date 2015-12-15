from pyVmomi import vim
import requests
import atexit
from qualipy.api.cloudshell_api import *
import qualipy.scripts.cloudshell_scripts_helpers as helpers
import time
import sys
import pycommon
from vCenterShell.pycommon.common_name_utils import generate_unique_name
from vCenterShell.pycommon.cloudshellDataRetrieverService import *
from vCenterShell.commands.baseCommand import BaseCommand
from timeit import default_timer as timer

class deployFromTemplateCommand(BaseCommand):
    """ Command to Create a VM from a template """


    def __init__(self, pvService, csRetrieverService):
        """
        :param pvService:   pyVmomiService Instance
        """
        self.pvService = pvService
        self.csRetrieverService = csRetrieverService

    def execute(self):
        """ execute the command """

        resource_att = helpers.get_resource_context_details()        

        # get vCenter resource name, template name, template folder
        templateModel = self.csRetrieverService.getVCenterTemplateAttributeData(resource_att)
        print "Template: {0}, Folder: {1}, vCenter: {2}".format(templateModel.template_name, templateModel.vm_folder, templateModel.vCenter_resource_name)
    
        # get power state of the cloned VM
        power_on = self.csRetrieverService.getPowerStateAttributeData(resource_att)
        print "Power On: {0}".format(power_on)

        # get cluster and resource pool
        vmClusterModel = self.csRetrieverService.getVMClusterAttributeData(resource_att)
        print "Cluster: {0}, Resource Pool: {1}".format(vmClusterModel.cluster_name, vmClusterModel.resource_pool)

        # get datastore
        datastore_name = self.csRetrieverService.getVMStorageAttributeData(resource_att)
        print "Datastore: {0}".format(datastore_name)


        reservation_id = helpers.get_reservation_context_details().id
        session = helpers.get_api_session()
        vCenter_details = session.GetResourceDetails(templateModel.vCenter_resource_name)
    
        # get vCenter connection details from vCenter resource
        vCenterConn = self.csRetrieverService.getVCenterConnectionDetails(session, vCenter_details)
        print "Connecting to: {0}, As: {1}, Pwd: {2}".format(vCenterConn["vCenter_url"] , vCenterConn["user"], vCenterConn["password"])
 
        # connect
        si = self.pvService.connect(vCenterConn["vCenter_url"] , vCenterConn["user"], vCenterConn["password"])
        content = si.RetrieveContent()

        start = timer()
        template = self.pvService.get_obj(content, [vim.VirtualMachine], templateModel.template_name)
        end = timer()
        print "Template search took {0} seconds".format(end - start)
    
        if not template:
            raise ValueError("template with name '{0}' not found".format(templateModel.template_name))

            # generate unique name
        vm_name = generate_unique_name(templateModel.template_name)

            vm = self.pvService.clone_vm(
                content = content, 
                si = si,
                template = template, 
                vm_name = vm_name,
                datacenter_name = None, 
            vm_folder = templateModel.vm_folder, 
                datastore_name = datastore_name, 
            cluster_name = vmClusterModel.cluster_name,
            resource_pool = vmClusterModel.resource_pool,
                power_on = power_on)

        session.CreateResource("Virtual Machine",
                                "Virtual Machine", 
                                vm_name,
                                vm_name)
        session.AddResourcesToReservation(reservation_id, [vm_name])
        session.SetAttributesValues(
                    [ResourceAttributesUpdateRequest(vm_name, 
                    [AttributeNameValue("vCenter Inventory Path", templateModel.vCenter_resource_name + "/" + templateModel.vm_folder),
                        AttributeNameValue("UUID", vm.summary.config.instanceUuid),
                        AttributeNameValue("vCenter Template", resource_att.attributes["vCenter Template"])])])

        # disconnect
        self.pvService.disconnect(si)


    
        
        

  



