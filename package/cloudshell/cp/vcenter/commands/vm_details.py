import traceback
import time

from cloudshell.cp.core.models import  VmDetailsProperty,VmDetailsData


class VmDetailsCommand(object):
    def __init__(self, pyvmomi_service, vm_details_provider):
        self.pyvmomi_service = pyvmomi_service
        self.vm_details_provider = vm_details_provider
        self.timeout = 30
        self.delay = 1

    def get_vm_details(self, si, logger, resource_context, requests, cancellation_context):
        results = []

        for request in requests:
            if cancellation_context.is_cancelled:
                break

            app_name = request.deployedAppJson.name

            try:
                vm = self.pyvmomi_service.find_by_uuid(si, request.deployedAppJson.vmdetails.uid)

                wait_for_ip = next((p.value for p in request.deployedAppJson.vmdetails.vmCustomParams if p.name == 'wait_for_ip'), 'False')

                self._wait_for_vm_to_be_ready(vm, request, logger)

                result = self.vm_details_provider.create(
                    vm=vm,
                    name=app_name,
                    reserved_networks=resource_context.attributes.get('Reserved Networks', '').split(';'),
                    ip_regex=next((p.value for p in request.deployedAppJson.vmdetails.vmCustomParams if p.name=='ip_regex'), None),
                    deployment_details_provider=DeploymentDetailsProviderFromAppJson(request.appRequestJson.deploymentService),
                    wait_for_ip=wait_for_ip,
                    logger=logger)

            except Exception as e:
                logger.error("Error getting vm details for '{0}': {1}".format(app_name, traceback.format_exc()))
                result = VmDetailsData(errorMessage=e.message)

            result.appName = app_name
            results.append(result)

        return results

    def _wait_for_vm_to_be_ready(self, vm, request, logger):
        start_time = time.time()
        while time.time()-start_time<self.timeout and (self._not_guest_net(vm) or self._no_guest_ip(vm, request)):
            time.sleep(self.delay)
        logger.info('_wait_for_vm_to_be_ready: '+str(time.time()-start_time)+' sec')

    @staticmethod
    def _not_guest_net(vm):
        return not vm.guest.net

    @staticmethod
    def _no_guest_ip(vm, request):
        wait_for_ip = next((p.value for p in request.deployedAppJson.vmdetails.vmCustomParams if p.name == 'wait_for_ip'), False)
        return wait_for_ip and not vm.guest.ipAddress


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
            data.append(VmDetailsProperty(key='Cloned VM Name',value= self.dep_attributes.get('vCenter VM','')))

        if self.deployment == 'VCenter Deploy VM From Linked Clone':
            template = self.dep_attributes.get('vCenter VM','')
            snapshot = self.dep_attributes.get('vCenter VM Snapshot','')
            data.append(VmDetailsProperty(key='Cloned VM Name',value= '{0} (snapshot: {1})'.format(template, snapshot)))

        if self.deployment == 'vCenter VM From Image':
            data.append(VmDetailsProperty(key='Base Image Name',value= self.dep_attributes.get('vCenter Image','').split('/')[-1]))

        if self.deployment == 'vCenter VM From Template':
            data.append(VmDetailsProperty(key='Template Name',value= self.dep_attributes.get('vCenter Template','')))

        return data