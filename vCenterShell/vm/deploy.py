import time

from models.DeployResultModel import DeployResult


class VirtualMachineDeployer(object):
    def __init__(self, pv_service, name_generator):
        self.pv_service = pv_service
        self.name_generator = name_generator

    def deploy_from_template(self, si, data_holder):

        # generate unique name
        vm_name = self.name_generator(data_holder.template_model.template_name)

        params = self.pv_service.CloneVmParameters(si=si,
                                                   template_name=data_holder.template_model.template_name,
                                                   vm_name=vm_name,
                                                   vm_folder=data_holder.template_model.vm_folder,
                                                   datastore_name=data_holder.datastore_name,
                                                   cluster_name=data_holder.vm_cluster_model.cluster_name,
                                                   resource_pool=data_holder.vm_cluster_model.resource_pool,
                                                   power_on=data_holder.power_on)

        clone_vm_result = self.pv_service.clone_vm(params)
        if clone_vm_result.error:
            raise Exception(clone_vm_result.error)

        deploy_result = DeployResult(vm_name, clone_vm_result.vm.summary.config.uuid,
                                     data_holder.template_model.vCenter_resource_name,
                                     data_holder.ip_regex)

        return deploy_result
