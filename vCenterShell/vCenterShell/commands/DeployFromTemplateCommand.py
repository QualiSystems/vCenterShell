from timeit import default_timer as timer
import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pyVmomi import vim
from qualipy.api.cloudshell_api import *
from vCenterShell.commands.BaseCommand1 import BaseCommand1
from vCenterShell.pycommon.common_name_utils import generate_unique_name


class DeployFromTemplateCommand(BaseCommand1):
    """ Command to Create a VM from a template """


    def __init__(self, pv_service, cs_retriever_service, resource_connection_details_retriever):
        """
        :param pvService:   pyVmomiService Instance
        """
        self.pv_service = pv_service
        self.cs_retriever_service = cs_retriever_service
        self.resource_connection_details_retriever = resource_connection_details_retriever

    def execute(self):
        """ execute the command """

        resource_att = helpers.get_resource_context_details()        

        # get vCenter resource name, template name, template folder
        template_model = self.cs_retriever_service.getVCenterTemplateAttributeData(resource_att)
        print "Template: {0}, Folder: {1}, vCenter: {2}".format(template_model.template_name, template_model.vm_folder, template_model.vCenter_resource_name)
    
        # get power state of the cloned VM
        power_on = self.cs_retriever_service.getPowerStateAttributeData(resource_att)
        print "Power On: {0}".format(power_on)

        # get cluster and resource pool
        vm_cluster_model = self.cs_retriever_service.getVMClusterAttributeData(resource_att)
        print "Cluster: {0}, Resource Pool: {1}".format(vm_cluster_model.cluster_name, vm_cluster_model.resource_pool)

        # get datastore
        datastore_name = self.cs_retriever_service.getVMStorageAttributeData(resource_att)
        print "Datastore: {0}".format(datastore_name)

        connection_details = self.resource_connection_details_retriever.get_connection_details(
                template_model.vCenter_resource_name)
        print "Connecting to: {0}, As: {1}, Pwd: {2}, Port: {3}".format(connection_details.host,
                                                                        connection_details.username,
                                                                        connection_details.password,
                                                                        connection_details.port)
 
        # connect
        si = self.pv_service.connect(connection_details.host, connection_details.username, connection_details.password,
                                     connection_details.port)
        content = si.RetrieveContent()

        start = timer()
        template = self.pv_service.get_obj(content, [vim.VirtualMachine], template_model.template_name)
        end = timer()
        print "Template search took {0} seconds".format(end - start)
    
        if not template:
            raise ValueError("template with name '{0}' not found".format(template_model.template_name))

        # generate unique name
        vm_name = generate_unique_name(template_model.template_name)

        vm = self.pv_service.clone_vm(
            content=content,
            si=si,
            template=template,
            vm_name=vm_name,
            datacenter_name=None,
            vm_folder=template_model.vm_folder,
            datastore_name=datastore_name,
            cluster_name=vm_cluster_model.cluster_name,
            resource_pool=vm_cluster_model.resource_pool,
            power_on=power_on)

        reservation_id = helpers.get_reservation_context_details().id
        session = helpers.get_api_session()
        session.CreateResource("Virtual Machine", "Virtual Machine", vm_name, vm_name)
        session.AddResourcesToReservation(reservation_id, [vm_name])
        session.SetAttributesValues(
                    [ResourceAttributesUpdateRequest(vm_name, 
                    [AttributeNameValue("vCenter Inventory Path", template_model.vCenter_resource_name + "/" + template_model.vm_folder),
                        AttributeNameValue("UUID", vm.summary.config.instanceUuid),
                        AttributeNameValue("vCenter Template", resource_att.attributes["vCenter Template"])])])

        # disconnect
        self.pv_service.disconnect(si)


    
        
        

  



