from cloudshell.cp.vcenter.models.DeployResultModel import DeployResult
from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from cloudshell.cp.vcenter.vm.ovf_image_params import OvfImageParams
from cloudshell.cp.vcenter.vm.vcenter_details_factory import VCenterDetailsFactory
from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation


class VirtualMachineDeployer(object):
    def __init__(self, pv_service, name_generator, ovf_service, cs_helper, resource_model_parser):
        """

        :param pv_service:
        :type pv_service: cloudshell.cp.vcenter.common.vcenter.vmomi_service.pyVmomiService
        :param name_generator:
        :param ovf_service:
        :type ovf_service: cloudshell.cp.vcenter.common.vcenter.ovf_service.OvfImageDeployerService
        :param cs_helper:
        :type resource_model_parser: ResourceModelParser
        :return:
        """
        self.pv_service = pv_service
        self.name_generator = name_generator
        self.ovf_service = ovf_service  # type common.vcenter.ovf_service.OvfImageDeployerService
        self.cs_helper = cs_helper  # type CloudshellDriverHelper
        self.resource_model_parser = resource_model_parser  # type ResourceModelParser

    def deploy_from_linked_clone(self, si, logger, data_holder, vcenter_data_model):
        """
        deploy Cloned VM From VM Command, will deploy vm from a snapshot

        :param si:
        :param logger:
        :type data_holder:
        :type vcenter_data_model:
        :return:
        """

        template_resource_model = data_holder.template_resource_model

        return self._deploy_a_clone(si,
                                    logger,
                                    data_holder.app_name,
                                    template_resource_model.vcenter_vm,
                                    template_resource_model,
                                    vcenter_data_model,
                                    snapshot=template_resource_model.vcenter_vm_snapshot)

    def deploy_clone_from_vm(self, si, logger, data_holder, vcenter_data_model):
        """
        deploy Cloned VM From VM Command, will deploy vm from another vm

        :param si:
        :param logger:
        :type data_holder:
        :type vcenter_data_model:
        :return:
        """
        template_resource_model = data_holder.template_resource_model
        return self._deploy_a_clone(si,
                                    logger,
                                    data_holder.app_name,
                                    template_resource_model.vcenter_vm,
                                    template_resource_model,
                                    vcenter_data_model)

    def deploy_from_template(self, si, logger, data_holder, vcenter_data_model):
        """
        :param si:
        :param logger:
        :type data_holder: DeployFromTemplateDetails
        :type vcenter_data_model
        :return:
        """
        template_resource_model = data_holder.template_resource_model
        return self._deploy_a_clone(si,
                                    logger,
                                    data_holder.app_name,
                                    template_resource_model.vcenter_template,
                                    template_resource_model,
                                    vcenter_data_model)

    def _deploy_a_clone(self, si, logger, app_name, template_name, other_params, vcenter_data_model, snapshot=''):
        # generate unique name
        vm_name = self.name_generator(app_name)

        VCenterDetailsFactory.set_deplyment_vcenter_params(
            vcenter_resource_model=vcenter_data_model, deploy_params=other_params)

        template_name = VMLocation.combine([other_params.default_datacenter,
                                            template_name])

        params = self.pv_service.CloneVmParameters(si=si,
                                                   template_name=template_name,
                                                   vm_name=vm_name,
                                                   vm_folder=other_params.vm_location,
                                                   datastore_name=other_params.vm_storage,
                                                   cluster_name=other_params.vm_cluster,
                                                   resource_pool=other_params.vm_resource_pool,
                                                   power_on=other_params.auto_power_on,
                                                   snapshot=snapshot)

        clone_vm_result = self.pv_service.clone_vm(clone_params=params, logger=logger)
        if clone_vm_result.error:
            raise Exception(clone_vm_result.error)

        return DeployResult(vm_name=vm_name,
                            vm_uuid=clone_vm_result.vm.summary.config.uuid,
                            cloud_provider_resource_name=other_params.vcenter_name,
                            ip_regex=other_params.ip_regex,
                            refresh_ip_timeout=other_params.refresh_ip_timeout,
                            auto_power_on=other_params.auto_power_on,
                            auto_power_off=other_params.auto_power_off,
                            wait_for_ip=other_params.wait_for_ip,
                            auto_delete=other_params.auto_delete,
                            autoload=other_params.autoload
                            )

    def deploy_from_image(self, si, logger, session, vcenter_data_model, data_holder, resource_context):
        vm_name = self.name_generator(data_holder.app_name)

        connection_details = self.cs_helper.get_connection_details(session=session,
                                                                   vcenter_resource_model=vcenter_data_model,
                                                                   resource_context=resource_context)

        VCenterDetailsFactory.set_deplyment_vcenter_params(vcenter_resource_model=vcenter_data_model,
                                                           deploy_params=data_holder.image_params)

        image_params = self._get_deploy_image_params(data_holder.image_params, connection_details, vm_name)

        res = self.ovf_service.deploy_image(vcenter_data_model, image_params, logger)
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
