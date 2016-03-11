from vCenterShell.models.DeployFromTemplateDetails import DeployFromTemplateDetails

class DeployCommand(object):
    """ Command to Create a VM from a template """

    def __init__(self, deployer):
        """
        :param deployer:   pv_service Instance
        """
        self.deployer = deployer

    def execute_deploy_from_template(self, si, deployment_params, resource_context):
        """

        :param si:
        :type deployment_params: DeployFromTemplateDetails
        :param resource_context:
        :return:
        """
        deploy_result = self.deployer.deploy_from_template(si, deployment_params, resource_context)
        return deploy_result

    def execute_deploy_from_image(self, si, session, vcenter_data_model, deployment_params, resource_context):
        deploy_result = self.deployer.deploy_from_image(si=si,
                                                        session=session,
                                                        vcenter_data_model=vcenter_data_model,
                                                        data_holder=deployment_params,
                                                        resource_context=resource_context)
        return deploy_result
