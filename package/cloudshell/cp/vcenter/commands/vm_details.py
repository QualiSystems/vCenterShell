import traceback

import jsonpickle

from cloudshell.cp.vcenter.vm.vm_details_provider import VmDetails


class VmDetailsCommand(object):
    def __init__(self, pyvmomi_service, vm_details_provider):
        self.pyvmomi_service = pyvmomi_service
        self.vm_details_provider = vm_details_provider

    def get_vm_details(self, si, logger, resource_context, requests, cancellation_context):
        results = []
        for request in requests:
            if cancellation_context.is_cancelled:
                break
            app_name = request.deployedAppJson.name
            try:
                #logger.info(jsonpickle.encode(request.appRequestJson))
                vm = self.pyvmomi_service.find_by_uuid(si, request.deployedAppJson.vmdetails.uid)
                result = self.vm_details_provider.create(
                    vm=vm,
                    name=app_name,
                    vcenter_attributes=resource_context.attributes,
                    vm_custom_params=dict((p.name,p.value) for p in request.deployedAppJson.vmdetails.vmCustomParams),
                    deployment_service=request.appRequestJson.deploymentService,
                    logger=logger)
            except Exception as e:
                logger.error("Error getting vm details for '{0}': {1}".format(app_name, traceback.format_exc()))
                result = VmDetails(app_name)
                result.error = e.message

            results.append(result)

        return results