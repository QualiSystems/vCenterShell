from unittest import TestCase

from mock import Mock

from models.DeployDataHolder import DeployDataHolder
from vCenterShell.vm.deploy import VirtualMachineDeployer


class TestVirtualMachineDeployer(TestCase):
    def test_vm_deployer(self):
        name = 'name'
        uuid = 'uuid'
        name_gen = Mock(return_value=name)
        pv_service = Mock()
        si = Mock()
        clone_parmas = Mock()
        clone_res = Mock()
        clone_res.error = None
        clone_res.vm = Mock()
        clone_res.vm.summary = Mock()
        clone_res.vm.summary.config = Mock()
        clone_res.vm.summary.config.uuid = uuid

        pv_service.CloneVmParameters = Mock(return_value=clone_parmas)
        pv_service.clone_vm = Mock(return_value=clone_res)
        params = DeployDataHolder({
            "resource_context": None,
            "template_model": {
                "vCenter_resource_name": "vcenter_resource_name",
                "vm_folder": "vfolder_name",
                "template_name": "template_name"
            },
            "vm_cluster_model": {
                "cluster_name": "cluster_name",
                "resource_pool": "resource_pool"
            },
            "datastore_name": "datastore_name",
            "power_on": False
        })

        deployer = VirtualMachineDeployer(pv_service, name_gen)
        res = deployer.deploy_from_template(si, params)

        self.assertEqual(res.vm_name, name)
        self.assertEqual(res.uuid, uuid)
        self.assertEqual(res.cloud_provider_resource_name,
                         params.template_model.vCenter_resource_name)
        self.assertTrue(pv_service.CloneVmParameters.called)

    def test_vm_deployer_error(self):
        name = 'name'
        name_gen = Mock(return_value=name)
        pv_service = Mock()
        si = Mock()
        clone_parmas = Mock()
        clone_res = Mock()
        clone_res.error = Mock()

        pv_service.CloneVmParameters = Mock(return_value=clone_parmas)
        pv_service.clone_vm = Mock(return_value=clone_res)
        params = DeployDataHolder.create_from_params(
            template_model={
                "vCenter_resource_name": "vcenter_resource_name",
                "vm_folder": "vfolder_name",
                "template_name": "template_name"
            },
            vm_cluster_model={
                "cluster_name": "cluster_name",
                "resource_pool": "resource_pool"
            },
            datastore_name="datastore_name",
            power_on=False)

        deployer = VirtualMachineDeployer(pv_service, name_gen)

        self.assertRaises(Exception, deployer.deploy_from_template, si, params)
        self.assertTrue(pv_service.CloneVmParameters.called)
