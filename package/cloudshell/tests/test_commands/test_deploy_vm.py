import os
import sys
import unittest

from mock import Mock
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.vcenter.models.vCenterVMFromTemplateResourceModel import vCenterVMFromTemplateResourceModel

from cloudshell.cp.vcenter.commands.deploy_vm import DeployCommand


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

        template_resource_model = vCenterVMFromTemplateResourceModel()

        deploy_params = DeployFromTemplateDetails(template_resource_model, 'VM Deployment')

        deploy_command = DeployCommand(deployer)

        resource_context = Mock()

        # act
        result = deploy_command.execute_deploy_from_template(
            si=si,
            logger=Mock(),
            deployment_params=deploy_params,
            vcenter_data_model=Mock())

        # assert
        self.assertTrue(result)
        self.assertTrue(deployer.deploy_from_template.called_with(si, deploy_params, resource_context))

    def test_deploy_image_execute(self):
        deployer = Mock()
        si = Mock()
        deployment_params = Mock()
        connectivity = Mock()
        res = Mock()
        deployer.deploy_from_image = Mock(return_value=res)
        session = Mock()
        vcenter_data_model = Mock()

        deploy_command = DeployCommand(deployer)

        # act
        result = deploy_command.execute_deploy_from_image(si=si,
                                                          logger=Mock(),
                                                          session=session,
                                                          vcenter_data_model=vcenter_data_model,
                                                          deployment_params=deployment_params,
                                                          resource_context=connectivity)

        # assert
        self.assertTrue(result)
        self.assertTrue(deployer.deploy_from_image.called_with(si, deployment_params, connectivity))

    def test_deploy_clone_execute(self):
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

        template_resource_model = vCenterVMFromTemplateResourceModel()

        deploy_params = DeployFromTemplateDetails(template_resource_model, 'VM Deployment')

        deploy_command = DeployCommand(deployer)

        resource_context = Mock()

        # act
        result = deploy_command.execute_deploy_clone_from_vm(
            si=si,
            logger=Mock(),
            vcenter_data_model=Mock(),
            deployment_params=deploy_params)

        # assert
        self.assertTrue(result)
        self.assertTrue(deployer.deploy_from_template.called_with(si, deploy_params, resource_context))

    def test_deploy_snapshot_execute(self):
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

        template_resource_model = vCenterVMFromTemplateResourceModel()

        deploy_params = DeployFromTemplateDetails(template_resource_model, 'VM Deployment')

        deploy_command = DeployCommand(deployer)

        resource_context = Mock()

        # act
        result = deploy_command.execute_deploy_from_linked_clone(
            si=si,
            logger=Mock(),
            deployment_params=deploy_params,
            vcenter_data_model=Mock())

        # assert
        self.assertTrue(result)
        self.assertTrue(deployer.deploy_from_template.called_with(si, deploy_params, resource_context))
