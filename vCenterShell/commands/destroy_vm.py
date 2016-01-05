import qualipy.scripts.cloudshell_scripts_helpers as helpers

from pycommon.logger import getLogger

logger = getLogger(__name__)


class DestroyVirtualMachineCommand(object):
    """ Command to Destroy a VM """

    def __init__(self, pvService, cloudshell_data_retriever_service):
        """
        :param pvService:   pyVmomiService Instance
        """
        self.pvService = pvService
        self.csRetrieverService = cloudshell_data_retriever_service

    def execute(self):
        """ execute the command """

        resource_att = helpers.get_resource_context_details()

        # get vCenter resource name
        inventory_path_data = self.csRetrieverService.getVCenterInventoryPathAttributeData(resource_att)
        vCenter_resource_name = inventory_path_data.vCenter_resource_name
        vm_folder = inventory_path_data.vm_folder

        logger.info("Folder: {0}, vCenter: {1}".format(vm_folder, vCenter_resource_name))

        reservation_id = helpers.get_reservation_context_details().id
        session = helpers.get_api_session()
        vCenter_details = session.GetResourceDetails(vCenter_resource_name)

        # get vCenter connection details from vCenter resource
        conn_details = self.csRetrieverService.getVCenterConnectionDetails(session, vCenter_details)

        logger.info("Connecting to: {0}, As: {1}, Pwd: {2}".format(conn_details.host, conn_details.username,
                                                                   conn_details.password))

        # connect
        si = self.pvService.connect(conn_details.host, conn_details.username, conn_details.password)
        content = si.RetrieveContent()

        # destroy the vm
        vm_name = resource_att.name
        self.pvService.destroy_vm_by_name(content, si, vm_name)

        # disconnect
        self.pvService.disconnect(si)

        # delete resource 
        helpers.get_api_session() \
            .DeleteResource(resource_att.fullname)
