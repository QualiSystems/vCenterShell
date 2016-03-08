from common.vcenter.vm_location import VMLocation
from models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from models.vCenterVMFromTemplateResourceModel import vCenterVMFromTemplateResourceModel
from models.VCenterDetails import VCenterDetails


class VCenterDetailsFactory(object):

    @staticmethod
    def create_vcenter_details(vcenter_resource_model, vcenter_template_resource_model):
        """
        Merges
        :type vcenter_resource_model: VMwarevCenterResourceModel
        :type vcenter_template_resource_model:  vCenterVMFromTemplateResourceModel
        :param name:
        :rtype: VCenterDetails
        """
        # Override attributes
        vm_cluster = vcenter_template_resource_model.vm_cluster or vcenter_resource_model.vm_cluster
        vm_storage = vcenter_template_resource_model.vm_storage or vcenter_resource_model.vm_storage
        vm_resource_pool = vcenter_template_resource_model.vm_resource_pool or vcenter_resource_model.vm_resource_pool
        vm_location = vcenter_template_resource_model.vm_location or vcenter_resource_model.vm_location
        default_datacenter = vcenter_resource_model.default_datacenter

        if not vm_cluster:
            raise ValueError('VM Cluster is empty')
        if not vm_storage:
            raise ValueError('VM Storage is empty')
        if not vm_resource_pool:
            raise ValueError('VM Resource Pool is empty')
        if not vm_location:
            raise ValueError('VM Location is empty')
        if not default_datacenter:
            raise ValueError('Default Datacenter attribute on VMWare vCenter is empty')

        vm_location = VMLocation.combine([default_datacenter, vm_location])

        return VCenterDetails(
            vm_cluster=vm_cluster,
            vm_storage=vm_storage,
            vm_resource_pool=vm_resource_pool,
            vm_location=vm_location,
            default_datacenter=default_datacenter)
