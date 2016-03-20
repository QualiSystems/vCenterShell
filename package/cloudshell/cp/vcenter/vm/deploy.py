from cloudshell.cp.vcenter.models.DeployResultModel import DeployResult
from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from cloudshell.cp.vcenter.vm.ovf_image_params import OvfImageParams
from cloudshell.cp.vcenter.vm.vcenter_details_factory import VCenterDetailsFactory

from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation


class VirtualMachineDeployer(object):
    def __init__(self, pv_service, name_generator, ovf_service, cs_helper, resource_model_parser):
        """

        :param pv_service:
        :param name_generator:
        :param ovf_service:
        :param cs_helper:
        :type resource_model_parser: ResourceModelParser
        :return:
        """
        self.pv_service = pv_service
        self.name_generator = name_generator
        self.ovf_service = ovf_service  # type common.vcenter.ovf_service.OvfImageDeployerService
        self.cs_helper = cs_helper  # type CloudshellDriverHelper
        self.resource_model_parser = resource_model_parser  # type ResourceModelParser

    def deploy_from_template(self, si, data_holder, resource_context):
        """

        :param si:
        :type data_holder: DeployFromTemplateDetails
        :type resource_context
        :return:
        """
        # generate unique name
        vm_name = self.name_generator(data_holder.app_name)

        vcenter_resource_model = self.resource_model_parser.convert_to_resource_model(resource_context,
                                                                                      VMwarevCenterResourceModel)

        template_resource_model = data_holder.template_resource_model
        VCenterDetailsFactory.set_deplyment_vcenter_params(
            vcenter_resource_model=vcenter_resource_model, deploy_params=template_resource_model)

        template_name = VMLocation.combine([template_resource_model.default_datacenter,
                                            template_resource_model.vcenter_template])

        params = self.pv_service.CloneVmParameters(si=si,
                                                   template_name=template_name,
                                                   vm_name=vm_name,
                                                   vm_folder=template_resource_model.vm_location,
                                                   datastore_name=template_resource_model.vm_storage,
                                                   cluster_name=template_resource_model.vm_cluster,
                                                   resource_pool=template_resource_model.vm_resource_pool,
                                                   power_on=template_resource_model.auto_power_on)

        clone_vm_result = self.pv_service.clone_vm(params)
        if clone_vm_result.error:
            raise Exception(clone_vm_result.error)

        return DeployResult(vm_name=vm_name,
                            vm_uuid=clone_vm_result.vm.summary.config.uuid,
                            cloud_provider_resource_name=template_resource_model.vcenter_name,
                            ip_regex=template_resource_model.ip_regex,
                            refresh_ip_timeout=template_resource_model.refresh_ip_timeout,
                            auto_power_on=template_resource_model.auto_power_on,
                            auto_power_off=template_resource_model.auto_power_off,
                            wait_for_ip=template_resource_model.wait_for_ip,
                            auto_delete=template_resource_model.auto_delete,
                            autoload=template_resource_model.autoload
                            )

    def deploy_from_image(self, si, session, vcenter_data_model, data_holder, resource_context):
        vm_name = self.name_generator(data_holder.app_name)

        connection_details = self.cs_helper.get_connection_details(session=session,
                                                                   vcenter_resource_model=vcenter_data_model,
                                                                   resource_context=resource_context)

        VCenterDetailsFactory.set_deplyment_vcenter_params(vcenter_resource_model=vcenter_data_model,
                                                           deploy_params=data_holder.image_params)

        image_params = self._get_deploy_image_params(data_holder.image_params, connection_details, vm_name)

        res = self.ovf_service.deploy_image(vcenter_data_model, image_params)
        if res:
            vm_path = image_params.datacenter + '/' + \
                      image_params.vm_folder if hasattr(image_params, 'vm_folder') and image_params.vm_folder else ''
            vm = self.pv_service.find_vm_by_name(si, vm_path, vm_name)
            if vm:
                return DeployResult(vm_name=vm_name,
                                    vm_uuid=vm.config.uuid,
                                    cloud_provider_resource_name=data_holder.image_params.vcenter_name,
                                    ip_regex=data_holder.image_params.ip_regex,
                                    refresh_ip_timeout=data_holder.image_params.refresh_ip_timeout,
                                    auto_power_on=data_holder.image_params.auto_power_on,
                                    auto_power_off=data_holder.image_params.auto_power_off,
                                    wait_for_ip=data_holder.image_params.wait_for_ip,
                                    auto_delete=data_holder.image_params.auto_delete,
                                    autoload=data_holder.image_params.autoload)
            raise Exception('the deployed vm from image({0}/{1}) could not be found'.format(vm_path, vm_name))
        raise Exception('failed deploying image')

    @staticmethod
    def _get_deploy_image_params(data_holder, host_info, vm_name):
        """
        :type data_holder: models.vCenterVMFromImageResourceModel.vCenterVMFromImageResourceModel
        """
        image_params = OvfImageParams()
        if hasattr(data_holder, 'vcenter_image_arguments') and data_holder.vcenter_image_arguments:
            image_params.user_arguments = data_holder.vcenter_image_arguments
        if hasattr(data_holder, 'vm_location') and data_holder.vm_location:
            image_params.vm_folder = data_holder.vm_location.replace(data_holder.default_datacenter + '/', '')
        image_params.cluster = data_holder.vm_cluster
        image_params.resource_pool = data_holder.vm_resource_pool
        image_params.connectivity = host_info
        image_params.vm_name = vm_name
        image_params.datastore = data_holder.vm_storage
        image_params.datacenter = data_holder.default_datacenter
        image_params.image_url = data_holder.vcenter_image
        image_params.power_on = data_holder.auto_power_on
        image_params.vcenter_name = data_holder.vcenter_name
        return image_params
