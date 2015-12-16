import qualipy.scripts.cloudshell_scripts_helpers as helpers
from pycommon.CloudshellDataRetrieverService import *


class DestroyVirtualMachineCommand(object):
    """ Command to Destroy a VM """

    def __init__(self, pvService, cs_retriever_service, resource_connection_details_retriever):
        """
        :param pvService:   pyVmomiService Instance
        """
        self.pvService = pvService
        self.csRetrieverService = cs_retriever_service
        self.resource_connection_details_retriever = resource_connection_details_retriever

    def destroy_vm(self, connection_details, vm_name, vm_folder):
        si = None
        try:
            # connect
            si = self.pvService.connect(connection_details.host,
                                        connection_details.username,
                                        connection_details.password,
                                        connection_details.port)
            # destroy the vm
            self.pvService.destroy_vm_by_name(si, vm_name, vm_folder)
        finally:
            # disconnect
            if si:
                self.pvService.disconnect(si)

    def execute(self):
        """ execute the command """

        resource_context = helpers.get_resource_context_details()

        # get vCenter resource name
        inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_context)
        vcenter_resource_name = inventory_path_data["vCenter_resource_name"]
        vm_folder = inventory_path_data["vm_folder"]
        print "Folder: {0}, vCenter: {1}".format(vm_folder, vcenter_resource_name)

        # get vCenter connection details from vCenter resource
        connection_details = self.resource_connection_details_retriever.get_connection_details(vcenter_resource_name)
        print "Connecting to: {0}, As: {1}, Pwd: {2}, Port: {3}".format(connection_details.host,
                                                                        connection_details.username,
                                                                        connection_details.password,
                                                                        connection_details.port)
        self.destroy_vm(connection_details=connection_details,
                        vm_name=resource_context.name,
                        vm_folder=vm_folder)

        # delete resource 
        helpers.get_api_session() \
            .DeleteResource(resource_context.fullname)
