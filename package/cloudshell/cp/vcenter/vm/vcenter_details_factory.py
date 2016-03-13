from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation


class VCenterDetailsFactory(object):

    @staticmethod
    def set_deplyment_vcenter_params(vcenter_resource_model, deploy_params):
        """
        Sets the vcenter parameters if not already set at the deployment option
        :param deploy_params:  vCenterVMFromTemplateResourceModel or vCenterVMFromImageResourceModel
        :type vcenter_resource_model: VMwarevCenterResourceModel
        """
        # Override attributes
        deploy_params.vm_cluster = deploy_params.vm_cluster or vcenter_resource_model.vm_cluster
        deploy_params.vm_storage = deploy_params.vm_storage or vcenter_resource_model.vm_storage
        deploy_params.vm_resource_pool = deploy_params.vm_resource_pool or vcenter_resource_model.vm_resource_pool
        deploy_params.vm_location = deploy_params.vm_location or vcenter_resource_model.vm_location
        deploy_params.default_datacenter = vcenter_resource_model.default_datacenter

        if not deploy_params.vm_cluster:
            raise ValueError('VM Cluster is empty')
        if not deploy_params.vm_storage:
            raise ValueError('VM Storage is empty')
        if not deploy_params.vm_location:
            raise ValueError('VM Location is empty')
        if not deploy_params.default_datacenter:
            raise ValueError('Default Datacenter attribute on VMWare vCenter is empty')

        deploy_params.vm_location = VMLocation.combine([deploy_params.default_datacenter, deploy_params.vm_location])
