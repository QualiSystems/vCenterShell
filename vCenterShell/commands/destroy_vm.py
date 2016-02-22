from common.logger import getLogger

logger = getLogger(__name__)


class DestroyVirtualMachineCommand(object):
    """ Command to Destroy a VM """

    def __init__(self, pv_service, resource_remover, disconnector):
        """
        :param pv_service:   pv_service Instance
        :param resource_remover: CloudshellResourceRemover
        """
        self.pv_service = pv_service
        self.resource_remover = resource_remover
        self.disconnector = disconnector

    def destroy(self, si, session, vm_uuid, vm_name):
        # find vm
        vm = self.pv_service.find_by_uuid(si, vm_uuid)

        # todo: change it with the function form SergaiiT Branch
        # todo: alexa: check if I can refactor the disconnector so it will not request the vCenter resource name
        # disconnect all vnics before destroy
        self.disconnector.disconnect_all(si, vm_uuid, vm)

        # destroy vm
        result = self.pv_service.destroy_vm(vm)

        # delete resources
        self.resource_remover.remove_resource(session=session, resource_full_name=vm_name)
        return result
