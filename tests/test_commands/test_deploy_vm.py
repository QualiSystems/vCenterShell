import os
import sys
import unittest

from mock import Mock

from models.DeployDataHolder import DeployDataHolder
from vCenterShell.commands.deploy_vm import DeployFromTemplateCommand

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))


class TestDeployFromTemplateCommand(unittest.TestCase):
    def test_deploy_execute(self):
        # arrange
        resource_creator = Mock()
        deployer = Mock()
        si = Mock()
        template_model = Mock()

        deploy_res = dict()
        deploy_res['vm_path'] = 'path'
        deploy_res['vm_name'] = 'name'
        deploy_res['uuid'] = 'uuid'

        template_model.template_name = 'temp name'
        template_model.vm_folder = 'temp folder'
        deployer.deploy_from_template = Mock(return_value=deploy_res)
        resource_creator.create_resource_for_deployed_vm = Mock(return_value=True)

        deploy_params = DeployDataHolder.create_from_params(template_model,
                                                            'datastore_name',
                                                            'vm_cluster_model',
                                                            'power_on')

        deploy_command = DeployFromTemplateCommand(deployer, resource_creator)

        # act
        result = deploy_command.execute_deploy_from_template(si, deploy_params)

        # assert
        self.assertTrue(result)
        self.assertTrue(deployer.deploy_from_template.called_with(si, deploy_params))
        self.assertTrue(
            resource_creator.create_resource_for_deployed_vm.called_with(deploy_res['vm_path'],
                                                                         deploy_params.template_model.template_name,
                                                                         deploy_res['vm_name'],
                                                                         deploy_res['uuid']))
