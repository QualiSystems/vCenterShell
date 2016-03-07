from common.vcenter.vm_location import VMLocation
from models.DeployResultModel import DeployResult
from vCenterShell.vm.ovf_image_params import OvfImageParams


class VirtualMachineDeployer(object):
    def __init__(self, pv_service, name_generator, ovf_service, cs_helper):
        self.pv_service = pv_service
        self.name_generator = name_generator
        self.ovf_service = ovf_service  # type common.vcenter.ovf_service.OvfImageDeployerService
        self.cs_helper = cs_helper  # type CloudshellDriverHelper

    def deploy_from_template(self, si, data_holder):
        # generate unique name
        vm_name = self.name_generator(data_holder.template_model.app_name)

        vm_folder = VMLocation.combine([data_holder.template_model.default_datacenter,
                                        data_holder.template_model.vm_folder])

        params = self.pv_service.CloneVmParameters(si=si,
                                                   template_name=data_holder.template_model.template_name,
                                                   vm_name=vm_name,
                                                   vm_folder=vm_folder,
                                                   datastore_name=data_holder.datastore_name,
                                                   cluster_name=data_holder.vm_cluster_model.cluster_name,
                                                   resource_pool=data_holder.vm_cluster_model.resource_pool,
                                                   power_on=data_holder.power_on)

        clone_vm_result = self.pv_service.clone_vm(params)
        if clone_vm_result.error:
            raise Exception(clone_vm_result.error)

        return DeployResult(vm_name,
                            clone_vm_result.vm.summary.config.uuid,
                            data_holder.template_model.vCenter_resource_name,
                            data_holder.ip_regex,
                            data_holder.refresh_ip_timeout)

    def deploy_from_image(self, si, session, vcenter_data_model, data_holder, resource_context):
        vm_name = self.name_generator(data_holder.app_name)

        connection_details = self.cs_helper.get_connection_details(session=session,
                                                                   vcenter_resource_model=vcenter_data_model,
                                                                   resource_context=resource_context)

        image_params = self._get_deploy_image_params(data_holder, connection_details, vm_name)

        res = self.ovf_service.deploy_image(vcenter_data_model, image_params)
        if res:
            vm_path = image_params.datacenter + '/' + \
                      image_params.vm_folder if hasattr(image_params, 'vm_name') and image_params.vm_folder else ''
            vm = self.pv_service.find_vm_by_name(si, vm_path, vm_name)
            if vm:
                return DeployResult(vm_name,
                                    vm.config.uuid,
                                    data_holder.vcenter_name,
                                    data_holder.ip_regex,
                                    data_holder.refresh_ip_timeout)
            raise Exception('the deployed vm from image({0}/{1}) could not be found'.format(vm_path, vm_name))
        raise Exception('failed deploying image')

    @staticmethod
    def _get_deploy_image_params(data_holder, host_info, vm_name):
        image_params = OvfImageParams()
        if hasattr(data_holder, 'user_arguments') and data_holder.user_arguments:
            image_params.user_arguments = data_holder.user_arguments
        if hasattr(data_holder, 'vm_folder') and data_holder.vm_folder:
            image_params.vm_folder = data_holder.vm_folder
        image_params.cluster = data_holder.cluster_name
        image_params.resource_pool = data_holder.resource_pool
        image_params.connectivity = host_info
        image_params.vm_name = vm_name
        image_params.datastore = data_holder.datastore_name
        image_params.datacenter = data_holder.datacenter_name
        image_params.image_url = data_holder.image_url
        image_params.power_on = data_holder.power_on
        image_params.vcenter_name = data_holder.vcenter_name
        return image_params
