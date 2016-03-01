

class DeployCommand(object):
    """ Command to Create a VM from a template """

    def __init__(self, deployer):
        """
        :param deployer:   pv_service Instance
        """
        self.deployer = deployer

    def execute_deploy_from_template(self, si, deployment_params):
        deploy_result = self.deployer.deploy_from_template(si, deployment_params)
        return deploy_result

    def execute_deploy_from_image(self, si, session, vcenter_data_model, deployment_params, resource_context):
        deploy_result = self.deployer.deploy_from_image(si, session, deployment_params, resource_context,
                                                        vcenter_data_model)
        return deploy_result
