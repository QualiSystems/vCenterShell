
class VmDetailsCommand(object):
    def __init__(self, pyvmomi_service, vm_details_provider):
        self.pyvmomi_service = pyvmomi_service
        self.vm_details_provider = vm_details_provider

    def get_vm_details(self, si, logger, resource_model):
        vm = self.pyvmomi_service.find_by_uuid(si, resource_model.vm_uuid)
        return self.vm_details_provider.create(vm, resource_model, logger)