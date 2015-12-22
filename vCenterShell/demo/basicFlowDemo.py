import time

import qualipy.scripts.cloudshell_dev_helpers as dev_helpers
import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim
from pycommon.CloudshellDataRetrieverService import *

from pycommon.common_name_utils import generate_unique_name


def run(pvService, cloudshellConnectData):
    """
    Create a VM, sleep, and destroy the VM

    pvService:              pyVmomiService Instance
    cloudshellConnectData:  dictionary with cloudshell connection data
    """

    csRetrieverService = CloudshellDataRetrieverService()

    dev_helpers.attach_to_cloudshell_as(cloudshellConnectData["user"], 
                                        cloudshellConnectData["password"], 
                                        cloudshellConnectData["domain"], 
                                        cloudshellConnectData["reservationId"])
    resource_att = helpers.get_resource_context_details()
        

    # get vCenter resource name, template name, template folder
    vCenterTemplateAttData = csRetrieverService.getVCenterTemplateAttributeData(resource_att)
    template_name = vCenterTemplateAttData["template_name"]
    vCenter_resource_name = vCenterTemplateAttData["vCenter_resource_name"]
    vm_folder = vCenterTemplateAttData["vm_folder"]
    print "Template: {0}, Folder: {1}, vCenter: {2}".format(template_name,vm_folder,vCenter_resource_name)
    

    # get power state of the cloned VM
    power_on = csRetrieverService.getPowerStateAttributeData(resource_att)
    print "Power On: {0}".format(power_on)


    # get cluster and resource pool
    vmClusterAttData = csRetrieverService.getVMClusterAttributeData(resource_att)
    cluster_name = vmClusterAttData["cluster_name"]
    resource_pool = vmClusterAttData["resource_pool"]
    print "Cluster: {0}, Resource Pool: {1}".format(cluster_name, resource_pool)


    # get datastore
    datastore_name = csRetrieverService.getVMStorageAttributeData(resource_att)
    print "Datastore: {0}".format(datastore_name)


    reservation_id = helpers.get_reservation_context_details().id
    session = helpers.get_api_session()
    vCenter_details = session.GetResourceDetails(vCenter_resource_name)
    
    # get vCenter connection details from vCenter resource
    vCenterConn = csRetrieverService.getVCenterConnectionDetails(session, vCenter_details)
    print "Connecting to: {0}, As: {1}, Pwd: {2}".format(vCenterConn["vCenter_url"] , vCenterConn["user"], vCenterConn["password"])
 
    # connect
    si = pvService.connect(vCenterConn["vCenter_url"] , vCenterConn["user"], vCenterConn["password"])
    content = si.RetrieveContent()
    template = pvService.get_obj(content, [vim.VirtualMachine], template_name)
    
    if template:
        # generate unique name
        vm_name = generate_unique_name(template_name)

        vm = pvService.clone_vm(
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
                            "Virtual Machine", vm_name,
                            vm.summary.config.instanceUuid)
        helpers.get_api_session() \
            .AddResourcesToReservation(reservation_id, [vm_name])
        helpers.get_api_session() \
            .SetAttributeValue(vm_name,
                               "vCenter Inventory Path",
                               attributeValue = vCenter_resource_name + "/" + vm_folder)


        sleep_sec = 5
        print "Sleep for {0} sec".format(sleep_sec)
        time.sleep( sleep_sec )

        
        # delete the VM and delete resource
        pvService.destroy_vm(content, si, vm)
        helpers.get_api_session().DeleteResource(vm_name)

    else:
        print "template not found"

    pvService.disconnect(si)
  
