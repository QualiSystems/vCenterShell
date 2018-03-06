from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails


class DeployCommand(object):
    """ Command to Create a VM from a template """

    def __init__(self, deployer):
        """
        :param deployer:   pv_service Instance
        :type deployer:   cloudshell.cp.vcenter.vm.deploy.VirtualMachineDeployer
        """
        self.deployer = deployer

    def execute_deploy_from_linked_clone(self, si, logger, vcenter_data_model, reservation_id, deployment_params, cancellation_context):
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
        deploy_result = self.deployer.deploy_from_linked_clone(si, logger, deployment_params, vcenter_data_model,
                                                               reservation_id, cancellation_context)
        return deploy_result

    def execute_deploy_clone_from_vm(self, si, logger, vcenter_data_model, reservation_id, deployment_params, cancellation_context):
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
        deploy_result = self.deployer.deploy_clone_from_vm(si, logger, deployment_params, vcenter_data_model,
                                                           reservation_id, cancellation_context)
        return deploy_result

    def execute_deploy_from_template(self, si, logger, vcenter_data_model, reservation_id, deployment_params, cancellation_context):
        """

        :param str reservation_id:
        :param si:
        :param logger:
        :type deployment_params: DeployFromTemplateDetails
        :param vcenter_data_model:
        :return:
        """
        deploy_result = self.deployer.deploy_from_template(si, logger, deployment_params, vcenter_data_model,
                                                           reservation_id, cancellation_context)
        return deploy_result

    def execute_deploy_from_image(self, si, logger, session, vcenter_data_model, reservation_id, deployment_params,
                                  resource_context, cancellation_context):
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
        deploy_result = self.deployer.deploy_from_image(si=si,
                                                        logger=logger,
                                                        session=session,
                                                        vcenter_data_model=vcenter_data_model,
                                                        data_holder=deployment_params,
                                                        resource_context=resource_context,
                                                        reservation_id=reservation_id,
                                                        cancellation_context=cancellation_context)
        return deploy_result
