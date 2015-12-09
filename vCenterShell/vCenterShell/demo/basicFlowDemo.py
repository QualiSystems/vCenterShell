from pyVmomi import vim
import requests
import atexit
from qualipy.api.cloudshell_api import *
import qualipy.scripts.cloudshell_scripts_helpers as helpers
import qualipy.scripts.cloudshell_dev_helpers as dev_helpers
import time
import uuid
import sys
import pycommon
from pycommon.common_collection_utils import first_or_default


def run(pvService, reservationId):
    """
    Create a VM, sleep, and destroy the VM

    cp:             CommonPyVmomi Instance
    reservationId:  Reservation id to attach
    """


    #si = pvService.connect("192.168.42.110", "qualisystems\\alex.az", "Freed0m!21")
    #content = si.RetrieveContent()


    dev_helpers.attach_to_cloudshell_as("admin","admin","Global",reservationId)
    resource_att = helpers.get_resource_context_details()
        

    # get vCenter resource name, template name, template folder
    template_att = resource_att.attributes["vCenter Template"]
    template_components = template_att.split("/")
    template_name = template_components[-1]
    vCenter_resource_name =template_components[0]
    vm_folder = template_components[1:-1][0]
    print "Template: {0}, Folder: {1}, vCenter: {2}".format(template_name,vm_folder,vCenter_resource_name)
    

    # get power state of the cloned VM
    power_on = False
    if resource_att.attributes["VM Power State"].lower() == "true":
        power_on = True
    print "Power On: {0}".format(power_on)


    # get cluster and resource pool
    cluster_name = None
    resource_pool = None
    storage_att = resource_att.attributes["VM Cluster"]
    if storage_att:
        storage_att_components = storage_att.split("/")
        if len(storage_att_components) == 2:
            cluster_name = storage_att_components[0]
            resource_pool = storage_att_components[1]
    print "Cluster: {0}, Resource Pool: {1}".format(cluster_name, resource_pool)


    # get datastore
    datastore_name = resource_att.attributes["VM Storage"]
    if not datastore_name:
        datastore_name = None
    print "Datastore: {0}".format(datastore_name)


    reservation_id = helpers.get_reservation_context_details().id
    session = helpers.get_api_session()
    vCenter_details = session.GetResourceDetails(vCenter_resource_name)
    
    # get vCenter connection details from vCenter resource
    user = first_or_default(vCenter_details.ResourceAttributes, lambda att: att.Name == "User").Value
    encryptedPass = first_or_default(vCenter_details.ResourceAttributes, lambda att: att.Name == "Password").Value
    vcenter_url = vCenter_details.Address
    password = session.DecryptPassword(encryptedPass).Value    
    
    print "Connecting to: {0}, As: {1}, Pwd: {2}".format(vcenter_url,user,password)
 
    si = pvService.connect(vcenter_url, user, password)
    content = si.RetrieveContent()
    template = pvService.get_obj(content, [vim.VirtualMachine], template_name)
    
    if template:
        # generate unique name
        unique_id = str(uuid.uuid4())[:8]
        vm_name = template_name + "_" + unique_id

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
  
