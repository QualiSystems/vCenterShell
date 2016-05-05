from unittest import TestCase

from cloudshell.cp.vcenter.models.VMwarevCenterResourceModel import VMwarevCenterResourceModel
from mock import Mock
from cloudshell.cp.vcenter.models.DeployDataHolder import DeployDataHolder
from cloudshell.cp.vcenter.models.DeployFromTemplateDetails import DeployFromTemplateDetails
from cloudshell.cp.vcenter.models.VCenterDeployVMFromLinkedCloneResourceModel import VCenterDeployVMFromLinkedCloneResourceModel
from cloudshell.cp.vcenter.models.vCenterCloneVMFromVMResourceModel import vCenterCloneVMFromVMResourceModel
from cloudshell.cp.vcenter.models.vCenterVMFromTemplateResourceModel import vCenterVMFromTemplateResourceModel
from cloudshell.cp.vcenter.vm.deploy import VirtualMachineDeployer

from cloudshell.cp.vcenter.common.model_factory import ResourceModelParser


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
        self.cs_helper = Mock()
        self.model_parser = ResourceModelParser()
        self.deployer = VirtualMachineDeployer(self.pv_service, self.name_gen, self.image_deployer, self.cs_helper,
                                               self.model_parser)

    def test_vm_deployer(self):
        deploy_from_template_details = DeployFromTemplateDetails(vCenterVMFromTemplateResourceModel(), 'VM Deployment')
        deploy_from_template_details.template_resource_model.vcenter_name = 'vcenter_resource_name'

        resource_context = self._create_vcenter_resource_context()

        res = self.deployer.deploy_from_template(
            si=self.si,
            data_holder=deploy_from_template_details,
            vcenter_data_model=resource_context,
            logger=Mock())

        self.assertEqual(res.vm_name, self.name)
        self.assertEqual(res.vm_uuid, self.uuid)
        self.assertEqual(res.cloud_provider_resource_name, 'vcenter_resource_name')
        self.assertTrue(self.pv_service.CloneVmParameters.called)

    def test_clone_deployer(self):
        deploy_from_template_details = DeployFromTemplateDetails(vCenterCloneVMFromVMResourceModel(), 'VM Deployment')
        deploy_from_template_details.template_resource_model.vcenter_name = 'vcenter_resource_name'
        deploy_from_template_details.vcenter_vm = 'name'
        resource_context = self._create_vcenter_resource_context()

        res = self.deployer.deploy_clone_from_vm(
            si=self.si,
            data_holder=deploy_from_template_details,
            vcenter_data_model=resource_context,
            logger=Mock())

        self.assertEqual(res.vm_name, self.name)
        self.assertEqual(res.vm_uuid, self.uuid)
        self.assertEqual(res.cloud_provider_resource_name, 'vcenter_resource_name')
        self.assertTrue(self.pv_service.CloneVmParameters.called)

    def test_snapshot_deployer(self):
        deploy_from_template_details = DeployFromTemplateDetails(VCenterDeployVMFromLinkedCloneResourceModel(), 'VM Deployment')
        deploy_from_template_details.template_resource_model.vcenter_name = 'vcenter_resource_name'
        deploy_from_template_details.vcenter_vm_snapshot = 'name/shanpshot'
        resource_context = self._create_vcenter_resource_context()

        res = self.deployer.deploy_from_linked_clone(
            si=self.si,
            data_holder=deploy_from_template_details,
            vcenter_data_model=resource_context,
            logger=Mock())

        self.assertEqual(res.vm_name, self.name)
        self.assertEqual(res.vm_uuid, self.uuid)
        self.assertEqual(res.cloud_provider_resource_name, 'vcenter_resource_name')
        self.assertTrue(self.pv_service.CloneVmParameters.called)

    def _create_vcenter_resource_context(self):
        vc = VMwarevCenterResourceModel()
        vc.user = 'user'
        vc.password = '123'
        vc.default_dvswitch = 'switch1'
        vc.holding_network = 'anetwork'
        vc.vm_cluster = 'Quali'
        vc.vm_location = 'Quali'
        vc.vm_resource_pool = 'Quali'
        vc.vm_storage = 'Quali'
        vc.shutdown_method = 'hard'
        vc.ovf_tool_path = 'C\\program files\ovf'
        vc.execution_server_selector = ''
        vc.reserved_networks = 'vlan65'
        vc.default_datacenter = 'QualiSB'

        return vc

    def test_vm_deployer_error(self):
        self.clone_res.error = Mock()

        self.pv_service.CloneVmParameters = Mock(return_value=self.clone_parmas)
        self.pv_service.clone_vm = Mock(return_value=self.clone_res)
        deploy_from_template_details = DeployFromTemplateDetails(vCenterVMFromTemplateResourceModel(), 'VM Deployment')
        deploy_from_template_details.template_resource_model.vcenter_name = 'vcenter_resource_name'

        vcenter_data_model = self._create_vcenter_resource_context()

        self.assertRaises(Exception, self.deployer.deploy_from_template, self.si,
                          Mock(), deploy_from_template_details, vcenter_data_model)
        self.assertTrue(self.pv_service.CloneVmParameters.called)

    def test_vm_deployer_image(self):
        params = DeployDataHolder({
            'app_name': 'appName',
            'vcenter_name': 'vCenter',
            'image_params':
                {
                    "vcenter_image": "c:\image.ovf",
                    "vm_cluster": "QualiSB Cluster",
                    "vm_resource_pool": "LiverPool",
                    "vm_storage": "eric ds cluster",
                    "default_datacenter": "QualiSB",
                    "vm_location": "vm_location",
                    "auto_power_on": 'False',
                    "vcenter_name": 'vCenter',
                    "vcenter_image_arguments": "--compress=9,--schemaValidate,--etc",
                    'ip_regex': '',
                    'refresh_ip_timeout': '10',
                    'auto_power_on': 'True',
                    'auto_power_off': 'True',
                    'wait_for_ip': 'True',
                    'auto_delete': 'True',
                    'autoload': 'True'
                }
        })

        connectivity = Mock()
        connectivity.address = 'vcenter ip or name'
        connectivity.user = 'user'
        connectivity.password = 'password'

        self.cs_helper.get_connection_details = Mock(return_value=connectivity)

        session = Mock()
        vcenter_data_model = Mock()
        vcenter_data_model.default_datacenter = 'qualisb'
        resource_context = Mock()

        res = self.deployer.deploy_from_image(si=self.si,
                                              logger=Mock(),
                                              session=session,
                                              vcenter_data_model=vcenter_data_model,
                                              data_holder=params,
                                              resource_context=resource_context)

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
