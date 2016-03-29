from cloudshell.cp.vcenter.common.vcenter.deployment_details import DeploymentDetails


class DeploymentDetailsFactory(object):
    @staticmethod
    def create_deployment_details(vcenter_resource_model, vm_cluster, vm_storage, vm_resource_pool, vm_location):
        """
        :type vcenter_resource_model: VMwarevCenterResourceModel
        :type vm_cluster: str
        :type vm_storage: str
        :type vm_resource_pool: str
        :type vm_location: str
        :rtype: DeploymentDetails
        """
        vm_cluster = vm_cluster or vcenter_resource_model.vm_cluster
        vm_storage = vm_storage or vcenter_resource_model.vm_storage
        vm_resource_pool = vm_resource_pool or vcenter_resource_model.vm_resource_pool
        vm_location = vm_location or vcenter_resource_model.vm_location

        return DeploymentDetails(
            vm_cluster=vm_cluster,
            vm_storage=vm_storage,
            vm_resource_pool=vm_resource_pool,
            vm_location=vm_location
        )
