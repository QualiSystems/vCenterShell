from unittest import TestCase
from mock import Mock
from models.DeployDataHolder import DeployDataHolder
from vCenterShell.vm.deploy import VirtualMachineDeployer


class TestVirtualMachineDeployer(TestCase):
    def setUp(self):
        self.name = 'name'
        self.uuid = 'uuid'
        self.name_gen = Mock(return_value=self.name)
        self.pv_service = Mock()
        self.si = Mock()
        self.clone_parmas = Mock()
        self.clone_res = Mock()
        self.clone_res.error = None
        self.clone_res.vm = Mock()
        self.clone_res.vm.summary = Mock()
        self.clone_res.vm.summary.config = Mock()
        self.clone_res.vm.summary.config.uuid = self.uuid
        self.pv_service.CloneVmParameters = Mock(return_value=self.clone_parmas)
        self.pv_service.clone_vm = Mock(return_value=self.clone_res)
        self.image_deployer = Mock()
        self.image_deployer.deploy_image = Mock(return_value=True)
        self.vm = Mock()
        self.vm.config = Mock()
        self.vm.config.uuid = self.uuid
        self.pv_service.find_vm_by_name = Mock(return_value=self.vm)
        self.deployer = VirtualMachineDeployer(self.pv_service, self.name_gen, self.image_deployer)

    def test_vm_deployer(self):
        params = DeployDataHolder({
            "resource_context": None,
            "template_model": {
                "vCenter_resource_name": "vcenter_resource_name",
                "vm_folder": "vfolder_name",
                "template_name": "template_name",
                "app_name": "some_name"
            },
            "vm_cluster_model": {
                "cluster_name": "cluster_name",
                "resource_pool": "resource_pool"
            },
            "datastore_name": "datastore_name",
            "power_on": False,
            'ip_regex': ''
        })

        res = self.deployer.deploy_from_template(self.si, params)

        self.assertEqual(res.vm_name, self.name)
        self.assertEqual(res.vm_uuid, self.uuid)
        self.assertEqual(res.cloud_provider_resource_name,
                         params.template_model.vCenter_resource_name)
        self.assertTrue(self.pv_service.CloneVmParameters.called)

    def test_vm_deployer_error(self):
        self.clone_res.error = Mock()

        self.pv_service.CloneVmParameters = Mock(return_value=self.clone_parmas)
        self.pv_service.clone_vm = Mock(return_value=self.clone_res)
        params = DeployDataHolder.create_from_params(
            template_model={
                "vCenter_resource_name": "vcenter_resource_name",
                "vm_folder": "vfolder_name",
                "template_name": "template_name",
                "app_name": "app_name"
            },
            vm_cluster_model={
                "cluster_name": "cluster_name",
                "resource_pool": "resource_pool"
            },
            datastore_name="datastore_name",
            power_on=False,
            ip_regex='')

        self.assertRaises(Exception, self.deployer.deploy_from_template, self.si, params)
        self.assertTrue(self.pv_service.CloneVmParameters.called)

    def test_vm_deployer_image(self):
        params = DeployDataHolder(
            {
                "image_url": "c:\image.ovf",
                "cluster_name": "QualiSB Cluster",
                "resource_pool": "LiverPool",
                "datastore_name": "eric ds cluster",
                "datacenter_name": "QualiSB",
                "power_on": False,
                "vcenter_name": 'vCenter',
                "app_name": "appName",
                "user_arguments": ["--compress=9",
                                   "--schemaValidate", "--etc"
                                   ],
                'ip_regex': ''
            })

        connectivity = Mock()
        connectivity.address = 'vcenter ip or name'
        connectivity.user = 'user'
        connectivity.password = 'password'

        res = self.deployer.deploy_from_image(self.si, params, connectivity)

        self.assertEqual(res.vm_name, self.name)
        self.assertEqual(res.vm_uuid, self.uuid)
        self.assertEqual(res.cloud_provider_resource_name,
                         params.vcenter_name)

    def test_vm_deployer_image_no_res(self):
        self.image_deployer.deploy_image = Mock(return_value=None)
        params = DeployDataHolder(
            {
                "image_url": "c:\image.ovf",
                "cluster_name": "QualiSB Cluster",
                "resource_pool": "LiverPool",
                "datastore_name": "eric ds cluster",
                "datacenter_name": "QualiSB",
                "power_on": False,
                "app_name": "appName",
                "user_arguments": ["--compress=9",
                                   "--schemaValidate", "--etc"
                                   ]
            })

        connectivity = Mock()
        connectivity.address = 'vcenter ip or name'
        connectivity.user = 'user'
        connectivity.password = 'password'

        self.assertRaises(Exception, self.deployer.deploy_from_image, self.si, params, connectivity)

    def test_vm_deployer_image_no_vm(self):
        self.pv_service.find_vm_by_name = Mock(return_value=None)
        params = DeployDataHolder(
            {
                "image_url": "c:\image.ovf",
                "cluster_name": "QualiSB Cluster",
                "resource_pool": "LiverPool",
                "datastore_name": "eric ds cluster",
                "datacenter_name": "QualiSB",
                "power_on": False,
                "app_name": "appName",
                "user_arguments": ["--compress=9",
                                   "--schemaValidate", "--etc"
                                   ]
            })

        connectivity = Mock()
        connectivity.address = 'vcenter ip or name'
        connectivity.user = 'user'
        connectivity.password = 'password'

        self.assertRaises(Exception, self.deployer.deploy_from_image, self.si, params, connectivity)
