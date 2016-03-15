from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.common_cloudshell_api import CloudShellAPIError

from cloudshell.cp.vcenter.common.logger import getLogger
from cloudshell.cp.vcenter.common.utilites.common_utils import get_error_message_from_exception

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

    def destroy(self, si, session, vcenter_data_model, vm_uuid, vm_name, reservation_id):
        """
        :param CloudShellAPISession session:
        :param str vm_name: This is the resource name
        :return:
        """
        # disconnect
        self._disconnect_all_my_connectors(session=session, resource_name=vm_name, reservation_id=reservation_id)
        # find vm
        vm = self.pv_service.find_by_uuid(si, vm_uuid)
        # destroy vm
        result = self.pv_service.destroy_vm(vm)
        # delete resources
        self.resource_remover.remove_resource(session=session, resource_full_name=vm_name)
        return result

    @staticmethod
    def _disconnect_all_my_connectors(session, resource_name, reservation_id):
        """
        :param CloudShellAPISession session:
        :param str resource_name:
        :param str reservation_id:
        """
        reservation_details = session.GetReservationDetails(reservation_id)
        connectors = reservation_details.ReservationDescription.Connectors
        endpoints = []
        for endpoint in connectors:
            if endpoint.Target == resource_name or endpoint.Source == resource_name:
                endpoints.append(endpoint.Target)
                endpoints.append(endpoint.Source)

        if len(endpoints) == 0:
            logger.info("No routes to disconnect for resource {0} in reservation {1}"
                        .format(resource_name, reservation_id))
            return

        logger.info("Executing disconnect routes for resource {0} in reservation {1}"
                    .format(resource_name, reservation_id))

        try:
            session.DisconnectRoutesInReservation(reservation_id, endpoints)
        except Exception as exc:
            logger.error("Error disconnecting routes for resource {0} in reservation {1}. Error: {2}"
                         .format(resource_name, reservation_id, get_error_message_from_exception(exc)))
