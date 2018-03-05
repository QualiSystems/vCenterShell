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
        logger = Mock()
        vcenter_data_model = Mock()
        reservation_id = Mock()
        cancellation_context = object()

        # act
        result = deploy_command.execute_deploy_from_template(
                si=si,
                logger=logger,
                deployment_params=deploy_params,
                vcenter_data_model=vcenter_data_model,
                reservation_id=reservation_id,
                cancellation_context=cancellation_context)

        # assert
        self.assertTrue(result)
        deployer.deploy_from_template.assert_called_once_with(si, logger, deploy_params, vcenter_data_model,
                                                              reservation_id, cancellation_context)

    def test_deploy_image_execute(self):
        deployer = Mock()
        si = Mock()
        deployment_params = Mock()
        connectivity = Mock()
        res = Mock()
        deployer.deploy_from_image = Mock(return_value=res)
        session = Mock()
        vcenter_data_model = Mock()
        logger = Mock()
        reservation_id = Mock()

        deploy_command = DeployCommand(deployer)
        cancellation_context = object()

        # act
        result = deploy_command.execute_deploy_from_image(si=si,
                                                          logger=logger,
                                                          session=session,
                                                          vcenter_data_model=vcenter_data_model,
                                                          deployment_params=deployment_params,
                                                          resource_context=connectivity,
                                                          reservation_id=reservation_id,
                                                          cancellation_context=cancellation_context)

        # assert
        self.assertTrue(result)
        deployer.deploy_from_image.assert_called_once_with(si=si,
                                                           logger=logger,
                                                           session=session,
                                                           vcenter_data_model=vcenter_data_model,
                                                           data_holder=deployment_params,
                                                           resource_context=connectivity,
                                                           reservation_id=reservation_id,
                                                           cancellation_context=cancellation_context)

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

        reservation_id = Mock()
        logger = Mock()
        vcenter_data_model = Mock()

        template_resource_model = vCenterVMFromTemplateResourceModel()

        deploy_params = DeployFromTemplateDetails(template_resource_model, 'VM Deployment')

        deploy_command = DeployCommand(deployer)

        resource_context = Mock()
        cancellation_context = object()

        # act
        result = deploy_command.execute_deploy_clone_from_vm(
                si=si,
                logger=logger,
                vcenter_data_model=vcenter_data_model,
                deployment_params=deploy_params,
                reservation_id=reservation_id,
                cancellation_context=cancellation_context)

        # assert
        self.assertTrue(result)
        deployer.deploy_clone_from_vm.assert_called_once_with(si, logger, deploy_params, vcenter_data_model,
                                                              reservation_id, cancellation_context)

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
        logger = Mock()
        vcenter_data_model = Mock()
        reservation_id = Mock()
        cancellation_context = object()

        # act
        result = deploy_command.execute_deploy_from_linked_clone(
                si=si,
                logger=logger,
                deployment_params=deploy_params,
                vcenter_data_model=vcenter_data_model,
                reservation_id=reservation_id,
                cancellation_context=cancellation_context)

        # assert
        self.assertTrue(result)
        deployer.deploy_from_linked_clone.assert_called_once_with(si, logger, deploy_params, vcenter_data_model,
                                                               reservation_id, cancellation_context)
