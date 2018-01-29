import traceback

import jsonpickle

from cloudshell.cp.vcenter.vm.vm_details_provider import VmDetails, VmDataField


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
                vm = self.pyvmomi_service.find_by_uuid(si, request.deployedAppJson.vmdetails.uid)
                result = self.vm_details_provider.create(
                    vm=vm,
                    name=app_name,
                    reserved_networks=resource_context.attributes.get('Reserved Networks', '').split(';'),
                    ip_regex=next((p.value for p in request.deployedAppJson.vmdetails.vmCustomParams if p.name=='ip_regex'), None),
                    deployment_details_provider=DeploymentDetailsProviderFromAppJson(request.appRequestJson.deploymentService),
                    logger=logger)
            except Exception as e:
                logger.error("Error getting vm details for '{0}': {1}".format(app_name, traceback.format_exc()))
                result = VmDetails(app_name)
                result.error = e.message

            results.append(result)

        return results


class DeploymentDetailsProviderFromAppJson(object):
    def __init__(self, deployment_service):
        self.deployment = deployment_service.model
        self.dep_attributes = dict((att.name, att.value) for att in deployment_service.attributes)

    def get_details(self):
        """
        :rtype list[VmDataField]
        """
        data = []
        if self.deployment == 'vCenter Clone VM From VM':
            data.append(VmDataField('Cloned VM Name', self.dep_attributes.get('vCenter VM', '').split('/')[-1]))

        if self.deployment == 'VCenter Deploy VM From Linked Clone':
            data.append(VmDataField('Cloned VM Name', self.dep_attributes.get('vCenter VM', '').split('/')[-1]))

        if self.deployment == 'vCenter VM From Image':
            data.append(VmDataField('Base Image Name', self.dep_attributes.get('vCenter Image', '').split('/')[-1]))

        if self.deployment == 'vCenter VM From Template':
            data.append(VmDataField('Template Name', self.dep_attributes.get('vCenter Template', '').split('/')[-1]))

        return data