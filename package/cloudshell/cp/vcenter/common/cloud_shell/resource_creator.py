# from cloudshell.api.cloudshell_api import ResourceAttributesUpdateRequest, AttributeNameValue

### NOT USED:
# class CloudshellResourceCreator(object):
#     def __init__(self, qualipy_helpers):
#         self.qualipy_helpers = qualipy_helpers
#
#     def create_resource_for_deployed_vm(self, path, vcenter_template, vm_name, vm_uuid):
#         reservation_id = self.qualipy_helpers.get_reservation_context_details().id
#         session = self.qualipy_helpers.get_api_session()
#         session.CreateResource('Virtual Machine', 'Virtual Machine', vm_name, vm_name)
#         session.AddResourcesToReservation(reservation_id, [vm_name])
#
#         session.SetAttributesValues(
#             [ResourceAttributesUpdateRequest(vm_name,
#                                              {AttributeNameValue('vCenter Inventory Path', path),
#                                               AttributeNameValue('UUID', vm_uuid),
#                                               AttributeNameValue('vCenter Template', vcenter_template)})])
