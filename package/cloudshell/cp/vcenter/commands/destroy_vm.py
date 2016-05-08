from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.cp.vcenter.common.utilites.common_utils import get_error_message_from_exception


class DestroyVirtualMachineCommand(object):
    """ Command to Destroy a VM """

    def __init__(self, pv_service, resource_remover, disconnector):
        """
        :param pv_service:   pv_service Instance
        :type pv_service:  cloudshell.cp.vcenter.common.vcenter.vmomi_service.pyVmomiService
        :param resource_remover: CloudshellResourceRemover
        """
        self.pv_service = pv_service
        self.resource_remover = resource_remover
        self.disconnector = disconnector

    def destroy(self, si, logger, session, vcenter_data_model, vm_uuid, vm_name, reservation_id):
        """
        :param si:
        :param logger:
        :param CloudShellAPISession session:
        :param vcenter_data_model:
        :param vm_uuid:
        :param str vm_name: This is the resource name
        :param reservation_id:
        :return:
        """
        # disconnect
        self._disconnect_all_my_connectors(session=session, resource_name=vm_name, reservation_id=reservation_id,
                                           logger=logger)
        # find vm
        vm = self.pv_service.find_by_uuid(si, vm_uuid)

        if vm is not None:
            # destroy vm
            result = self.pv_service.destroy_vm(vm=vm, logger=logger)
        else:
            logger.info("Could not find the VM {0},will remove the resource.".format(vm_name))
            result = True

        # delete resources
        self.resource_remover.remove_resource(session=session, resource_full_name=vm_name)
        return result

    def destroy_vm_only(self, si, logger, session, vcenter_data_model, vm_uuid, vm_name, reservation_id):
        """
        :param logger:
        :param CloudShellAPISession session:
        :param str vm_name: This is the resource name
        :return:
        """
        # disconnect
        self._disconnect_all_my_connectors(session=session,
                                           resource_name=vm_name,
                                           reservation_id=reservation_id,
                                           logger=logger)
        # find vm
        vm = self.pv_service.find_by_uuid(si, vm_uuid)
        if vm is not None:
            # destroy vm
            result = self.pv_service.destroy_vm(vm=vm,logger=logger)
        else:
            resource___format = "Could not find the VM {0},will remove the resource.".format(vm_name)
            logger.info(resource___format)
            result = resource___format

        return result

    @staticmethod
    def _disconnect_all_my_connectors(session, resource_name, reservation_id, logger):
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
