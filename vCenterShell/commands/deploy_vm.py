

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

    def execute_deploy_from_image(self, si, deployment_params, connectivity):
        deploy_result = self.deployer.deploy_from_image(si, deployment_params, connectivity)
        return deploy_result
