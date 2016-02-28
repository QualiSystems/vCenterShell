import os
import sys
import unittest

from mock import Mock

from models.DeployDataHolder import DeployDataHolder
from vCenterShell.commands.deploy_vm import DeployCommand

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))


class TestDeployFromTemplateCommand(unittest.TestCase):
    def test_deploy_execute(self):
        # arrange
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

        deploy_params = DeployDataHolder.create_from_params(template_model,
                                                            'datastore_name',
                                                            'vm_cluster_model',
                                                            'power_on',
                                                            'ip_regex')

        deploy_command = DeployCommand(deployer)

        # act
        result = deploy_command.execute_deploy_from_template(si, deploy_params)

        # assert
        self.assertTrue(result)
        self.assertTrue(deployer.deploy_from_template.called_with(si, deploy_params))

    def test_deploy_image_execute(self):
        deployer = Mock()
        si = Mock()
        deployment_params = Mock()
        connectivity = Mock()
        res = Mock()
        deployer.deploy_from_image = Mock(return_value=res)

        deploy_command = DeployCommand(deployer)

        # act
        result = deploy_command.execute_deploy_from_image(si, deployment_params, connectivity)

        # assert
        self.assertTrue(result)
        self.assertTrue(deployer.deploy_from_image.called_with(si, deployment_params, connectivity))
