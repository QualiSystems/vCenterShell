from cloudshell.cp.vcenter.models.DeployFromImageDetails import DeployFromImageDetails

from cloudshell.cp.vcenter.common.vcenter.vm_location import VMLocation
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from os.path import normpath

DEPLOYED_APPS = 'Deployed Apps'



class DeployCommand(object):
    """ Command to Create a VM from a template """

    def __init__(self, deployer):
        """
        :param deployer:   pv_service Instance
        :type deployer:   cloudshell.cp.vcenter.vm.deploy.VirtualMachineDeployer
        """
        self.deployer = deployer

    def execute_deploy_from_linked_clone(self, si, logger, vcenter_data_model, reservation_id, deployment_params, cancellation_context, folder_manager):
        """
        Calls the deployer to deploy vm from snapshot
        :param cancellation_context:
        :param str reservation_id:
        :param si:
        :param logger:
        :type deployment_params: DeployFromLinkedClone
        :param vcenter_data_model:
        :return:
        """
        self._prepare_deployed_apps_folder(deployment_params, si, logger, folder_manager, vcenter_data_model)

        deploy_result = self.deployer.deploy_from_linked_clone(si, logger, deployment_params, vcenter_data_model,
                                                               reservation_id, cancellation_context)
        return deploy_result

    def execute_deploy_clone_from_vm(self, si, logger, vcenter_data_model, reservation_id, deployment_params, cancellation_context, folder_manager):
        """
        Calls the deployer to deploy vm from another vm
        :param cancellation_context:
        :param str reservation_id:
        :param si:
        :param logger:
        :type deployment_params: DeployFromTemplateDetails
        :param vcenter_data_model:
        :return:
        """
        self._prepare_deployed_apps_folder(deployment_params, si, logger, folder_manager, vcenter_data_model)
        deploy_result = self.deployer.deploy_clone_from_vm(si, logger, deployment_params, vcenter_data_model,
                                                           reservation_id, cancellation_context)
        return deploy_result

    def _prepare_deployed_apps_folder(self, data_holder, si, logger, folder_manager, vcenter_resource_model):
        if isinstance(data_holder, DeployFromImageDetails):
            self._update_deploy_from_image_vm_location(data_holder, folder_manager, logger, si, vcenter_resource_model)
        else:
            self._update_deploy_from_template_vm_location(data_holder, folder_manager, logger, si,
                                                          vcenter_resource_model)

    def _update_deploy_from_template_vm_location(self, data_holder, folder_manager, logger, si, vcenter_resource_model):
        vm_location = data_holder.template_resource_model.vm_location or vcenter_resource_model.vm_location
        folder_path = VMLocation.combine([vcenter_resource_model.default_datacenter, vm_location])
        folder_manager.get_or_create_vcenter_folder(si,
                                                    logger,
                                                    folder_path,
                                                    DEPLOYED_APPS)
        data_holder.template_resource_model.vm_location = VMLocation.combine([vm_location, DEPLOYED_APPS])
        logger.info('VM will be deployed to {0}'.format(data_holder.template_resource_model.vm_location))

    def _update_deploy_from_image_vm_location(self, data_holder, folder_manager, logger, si, vcenter_resource_model):
        vm_location = data_holder.image_params.vm_location or vcenter_resource_model.vm_location
        folder_path = VMLocation.combine([vcenter_resource_model.default_datacenter, vm_location])
        folder_manager.get_or_create_vcenter_folder(si,
                                                    logger,
                                                    folder_path,
                                                    DEPLOYED_APPS)
        data_holder.image_params.vm_location = VMLocation.combine([vm_location, DEPLOYED_APPS])
        logger.info('VM will be deployed to {0}'.format(data_holder.image_params.vm_location))

    def execute_deploy_from_template(self, si, logger, vcenter_data_model, reservation_id, deployment_params, cancellation_context, folder_manager):
        """

        :param str reservation_id:
        :param si:
        :param logger:
        :type deployment_params: DeployFromTemplateDetails
        :param vcenter_data_model:
        :return:
        """
        self._prepare_deployed_apps_folder(deployment_params, si, logger, folder_manager, vcenter_data_model)

        deploy_result = self.deployer.deploy_from_template(si, logger, deployment_params, vcenter_data_model,
                                                           reservation_id, cancellation_context)
        return deploy_result

    def execute_deploy_from_image(self, si, logger, session, vcenter_data_model, reservation_id, deployment_params,
                                  resource_context, cancellation_context, folder_manager):
        """

        :param cancellation_context:
        :param str reservation_id:
        :param si:
        :param logger:
        :param session:
        :param vcenter_data_model:
        :param deployment_params:
        :param resource_context:
        :return:
        """
        self._prepare_deployed_apps_folder(deployment_params, si, logger, folder_manager, vcenter_data_model)

        deploy_result = self.deployer.deploy_from_image(si=si,
                                                        logger=logger,
                                                        session=session,
                                                        vcenter_data_model=vcenter_data_model,
                                                        data_holder=deployment_params,
                                                        resource_context=resource_context,
                                                        reservation_id=reservation_id,
                                                        cancellation_context=cancellation_context)
        return deploy_result
