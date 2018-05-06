import traceback

from cloudshell.cp.core.models import DeployAppResult
from cloudshell.cp.vcenter.models.VCenterDeployVMFromLinkedCloneResourceModel import \
    VCenterDeployVMFromLinkedCloneResourceModel
from cloudshell.cp.vcenter.models.DeployResultModel import DeployResult
from cloudshell.cp.vcenter.models.vCenterCloneVMFromVMResourceModel import vCenterCloneVMFromVMResourceModel
from cloudshell.cp.vcenter.models.vCenterVMFromImageResourceModel import vCenterVMFromImageResourceModel
from cloudshell.cp.vcenter.models.vCenterVMFromTemplateResourceModel import vCenterVMFromTemplateResourceModel
from cloudshell.cp.vcenter.vm.ovf_image_params import OvfImageParams
from cloudshell.cp.vcenter.vm.vcenter_details_factory import VCenterDetailsFactory
from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from cloudshell.cp.vcenter.common.cloud_shell.conn_details_retriever import ResourceConnectionDetailsRetriever
from cloudshell.cp.vcenter.vm.vm_details_provider import VmDataField


class VirtualMachineDeployer(object):
    def __init__(self, pv_service, name_generator, ovf_service, resource_model_parser, vm_details_provider):
        """

        :param pv_service:
        :type pv_service: cloudshell.cp.vcenter.common.vcenter.vmomi_service.pyVmomiService
        :param name_generator:
        :param ovf_service:
        :type ovf_service: cloudshell.cp.vcenter.common.vcenter.ovf_service.OvfImageDeployerService
        :type resource_model_parser: ResourceModelParser
        :param vm_details_provider:
        :type vm_details_provider: cloudshell.cp.vcenter.vm.vm_details_provider.VmDetailsProvider
        :return:
        """
        self.pv_service = pv_service
        self.name_generator = name_generator
        self.ovf_service = ovf_service  # type common.vcenter.ovf_service.OvfImageDeployerService
        self.resource_model_parser = resource_model_parser  # type ResourceModelParser
        self.vm_details_provider = vm_details_provider

    def deploy_from_linked_clone(self, si, logger, data_holder, vcenter_data_model, reservation_id,
                                 cancellation_context):
        """
        deploy Cloned VM From VM Command, will deploy vm from a snapshot

        :param cancellation_context:
        :param si:
        :param logger:
        :param data_holder:
        :param vcenter_data_model:
        :param str reservation_id:
        :rtype DeployAppResult:
        :return:
        """

        template_resource_model = data_holder.template_resource_model

        return self._deploy_a_clone(si=si,
                                    logger=logger,
                                    app_name=data_holder.app_name,
                                    template_name=template_resource_model.vcenter_vm,
                                    other_params=template_resource_model,
                                    vcenter_data_model=vcenter_data_model,
                                    reservation_id=reservation_id,
                                    cancellation_context=cancellation_context,
                                    snapshot=template_resource_model.vcenter_vm_snapshot)

    def deploy_clone_from_vm(self, si, logger, data_holder, vcenter_data_model, reservation_id, cancellation_context):
        """
        deploy Cloned VM From VM Command, will deploy vm from another vm

        :param cancellation_context:
        :param reservation_id:
        :param si:
        :param logger:
        :type data_holder:
        :type vcenter_data_model:
        :rtype DeployAppResult:
        :return:
        """
        template_resource_model = data_holder.template_resource_model
        return self._deploy_a_clone(si,
                                    logger,
                                    data_holder.app_name,
                                    template_resource_model.vcenter_vm,
                                    template_resource_model,
                                    vcenter_data_model,
                                    reservation_id,
                                    cancellation_context)

    def deploy_from_template(self, si, logger, data_holder, vcenter_data_model, reservation_id, cancellation_context):
        """
        :param cancellation_context:
        :param reservation_id:
        :param si:
        :param logger:
        :type data_holder: DeployFromTemplateDetails
        :type vcenter_data_model
        :rtype DeployAppResult:
        :return:
        """
        template_resource_model = data_holder.template_resource_model
        return self._deploy_a_clone(si,
                                    logger,
                                    data_holder.app_name,
                                    template_resource_model.vcenter_template,
                                    template_resource_model,
                                    vcenter_data_model,
                                    reservation_id,
                                    cancellation_context)

    def _deploy_a_clone(self, si, logger, app_name, template_name, other_params, vcenter_data_model, reservation_id,
                        cancellation_context,
                        snapshot=''):
        """
        :rtype DeployAppResult:
        """
        # generate unique name
        vm_name = self.name_generator(app_name, reservation_id)

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

        if cancellation_context.is_cancelled:
            raise Exception("Action 'Clone VM' was cancelled.")

        clone_vm_result = self.pv_service.clone_vm(clone_params=params, logger=logger,
                                                   cancellation_context=cancellation_context)
        if clone_vm_result.error:
            raise Exception(clone_vm_result.error)

        # remove a new created vm due to cancellation
        if cancellation_context.is_cancelled:
            self.pv_service.destroy_vm(vm=clone_vm_result.vm, logger=logger)
            raise Exception("Action 'Clone VM' was cancelled.")

        vm_details_data = self._safely_get_vm_details(clone_vm_result.vm, vm_name, vcenter_data_model, other_params,
                                                      logger)

        return DeployAppResult(vmName=vm_name,
                               vmUuid=clone_vm_result.vm.summary.config.uuid,
                               vmDetailsData=vm_details_data,
                               deployedAppAdditionalData={'ip_regex': other_params.ip_regex,
                                                          'refresh_ip_timeout': other_params.refresh_ip_timeout})

    def deploy_from_image(self, si, logger, session, vcenter_data_model, data_holder, resource_context, reservation_id,
                          cancellation_context):
        vm_name = self.name_generator(data_holder.app_name, reservation_id)

        connection_details = ResourceConnectionDetailsRetriever.get_connection_details(session=session,
                                                                                       vcenter_resource_model=vcenter_data_model,
                                                                                       resource_context=resource_context)

        VCenterDetailsFactory.set_deplyment_vcenter_params(vcenter_resource_model=vcenter_data_model,
                                                           deploy_params=data_holder.image_params)

        image_params = self._get_deploy_image_params(data_holder.image_params, connection_details, vm_name)

        if cancellation_context.is_cancelled:
            raise Exception("Action 'Deploy from image' was cancelled.")

        res = self.ovf_service.deploy_image(vcenter_data_model, image_params, logger)
        if res:
            vm_path = image_params.datacenter + '/' + \
                      image_params.vm_folder if hasattr(image_params, 'vm_folder') and image_params.vm_folder else ''
            vm = self.pv_service.find_vm_by_name(si, vm_path, vm_name)
            if vm:
                # remove a new created vm due to cancellation
                if cancellation_context.is_cancelled:
                    self.pv_service.destroy_vm(vm=vm, logger=logger)
                    raise Exception("Action 'Deploy from image' was cancelled.")

                vm_details_data = self._safely_get_vm_details(vm, vm_name, vcenter_data_model, data_holder.image_params,
                                                              logger)
                return DeployResult(vm_name=vm_name,
                                    vm_uuid=vm.config.uuid,
                                    cloud_provider_resource_name=data_holder.image_params.vcenter_name,
                                    ip_regex=data_holder.image_params.ip_regex,
                                    refresh_ip_timeout=data_holder.image_params.refresh_ip_timeout,
                                    auto_power_on=data_holder.image_params.auto_power_on,
                                    auto_power_off=data_holder.image_params.auto_power_off,
                                    wait_for_ip=data_holder.image_params.wait_for_ip,
                                    auto_delete=data_holder.image_params.auto_delete,
                                    autoload=data_holder.image_params.autoload,
                                    vm_details_data=vm_details_data)
            raise Exception('the deployed vm from image({0}/{1}) could not be found'.format(vm_path, vm_name))
        raise Exception('failed deploying image')

    def _safely_get_vm_details(self, vm, vm_name, vcenter_model, deploy_model, logger):
        data = None
        try:
            data = self.vm_details_provider.create(
                vm=vm,
                name=vm_name,
                reserved_networks=vcenter_model.reserved_networks,
                ip_regex=deploy_model.ip_regex,
                deployment_details_provider=DeploymentDetailsProviderFromTemplateModel(deploy_model),
                logger=logger)
        except Exception as e:
            logger.error("Error getting vm details for '{0}': {1}".format(vm_name, traceback.format_exc()))
        return data

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


class DeploymentDetailsProviderFromTemplateModel(object):
    def __init__(self, template_resource_model):
        self.model = template_resource_model

    def get_details(self):
        """
        :rtype list[VmDataField]
        """
        data = []
        if isinstance(self.model, vCenterCloneVMFromVMResourceModel):
            data.append(VmDataField('Cloned VM Name', self.model.vcenter_vm))

        if isinstance(self.model, VCenterDeployVMFromLinkedCloneResourceModel):
            template = self.model.vcenter_vm
            snapshot = self.model.vcenter_vm_snapshot
            data.append(VmDataField('Cloned VM Name', '{0} (snapshot: {1})'.format(template, snapshot)))

        if isinstance(self.model, vCenterVMFromImageResourceModel):
            data.append(VmDataField('Base Image Name', self.model.vcenter_image.split('/')[-1]))

        if isinstance(self.model, vCenterVMFromTemplateResourceModel):
            data.append(VmDataField('Template Name', self.model.vcenter_template))

        return data
