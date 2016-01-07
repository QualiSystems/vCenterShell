

class DeployFromTemplateCommand(object):
    """ Command to Create a VM from a template """

    def __init__(self, deployer, resource_creator):
        """
        :param pvService:   pv_service Instance
        """
        self.deployer = deployer
        self.resource_creator = resource_creator

    def execute_deploy_from_template(self, si, deployment_params):
        deploy_result = self.deployer.deploy_from_template(si, deployment_params)
        self.resource_creator.create_resource_for_deployed_vm(deploy_result['vm_path'],
                                                              deployment_params.template_model.template_name,
                                                              deploy_result['vm_name'],
                                                              deploy_result['uuid'])
        return deploy_result
