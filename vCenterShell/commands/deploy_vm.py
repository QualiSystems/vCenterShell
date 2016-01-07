

class DeployFromTemplateCommand(object):
    """ Command to Create a VM from a template """

    def __init__(self, deployer):
        """
        :param pvService:   pv_service Instance
        """
        self.deployer = deployer

    def execute_deploy_from_template(self, si, deployment_params):
        deploy_result = self.deployer.deploy_from_template(si, deployment_params)
        return deploy_result
