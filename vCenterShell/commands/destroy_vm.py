import qualipy.scripts.cloudshell_scripts_helpers as helpers
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

    def destroy(self, si, uuid, resource_full_name):
        # find vm
        vm = self.pv_service.find_by_uuid(si, uuid)

        # todo: change it with the function form SergaiiT Branch
        #disconnect all vnics
        self.disconnector.remove_interfaces_from_vm(vm)

        # destroy vm
        result = self.pv_service.destory_mv(si, vm)

        # delete resources
        self.resource_remover.remove_resource(resource_full_name)
        return result
