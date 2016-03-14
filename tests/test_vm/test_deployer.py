from unittest import TestCase

from cloudshell.api.cloudshell_api import ResourceInfo
from mock import Mock, create_autospec
from vCenterShell.models.DeployDataHolder import DeployDataHolder
from vCenterShell.models.vCenterVMFromTemplateResourceModel import vCenterVMFromTemplateResourceModel

from vCenterShell.common.model_factory import ResourceModelParser
from vCenterShell.models.DeployFromTemplateDetails import DeployFromTemplateDetails
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
        self.cs_helper = Mock()
        self.deployer = VirtualMachineDeployer(self.pv_service, self.name_gen, self.image_deployer, self.cs_helper,
                                               ResourceModelParser())

    def test_vm_deployer(self):
        deploy_from_template_details = DeployFromTemplateDetails(vCenterVMFromTemplateResourceModel(), 'VM Deployment')
        deploy_from_template_details.template_resource_model.vcenter_name = 'vcenter_resource_name'

        resource_context = self._create_vcenter_resource_context()

        res = self.deployer.deploy_from_template(
            si=self.si,
            data_holder=deploy_from_template_details,
            resource_context=resource_context)

        self.assertEqual(res.vm_name, self.name)
        self.assertEqual(res.vm_uuid, self.uuid)
        self.assertEqual(res.cloud_provider_resource_name, 'vcenter_resource_name')
        self.assertTrue(self.pv_service.CloneVmParameters.called)

    def _create_vcenter_resource_context(self):
        resource_context = create_autospec(ResourceInfo)
        resource_context.ResourceModelName = 'VMwarev Center'
        resource_context.ResourceAttributes = {'User': 'user',
                                               'Password': '123',
                                               'Default dvSwitch': 'switch1',
                                               'Holding Network': 'anetwork',
                                               'Default Port Group Location': 'Quali',
                                               'VM Cluster': 'Quali',
                                               'VM Location': 'Quali',
                                               'VM Resource Pool': 'Quali',
                                               'VM Storage': 'Quali',
                                               'Shutdown Method': 'hard',
                                               'OVF Tool Path': 'C\\program files\ovf',
                                               'Execution Server Selector': '',
                                               'Reserved Networks': 'vlan65',
                                               'Default Datacenter': 'QualiSB'
                                               }
        return resource_context

    def test_vm_deployer_error(self):
        self.clone_res.error = Mock()

        self.pv_service.CloneVmParameters = Mock(return_value=self.clone_parmas)
        self.pv_service.clone_vm = Mock(return_value=self.clone_res)
        deploy_from_template_details = DeployFromTemplateDetails(vCenterVMFromTemplateResourceModel(), 'VM Deployment')
        deploy_from_template_details.template_resource_model.vcenter_name = 'vcenter_resource_name'

        resource_context = self._create_vcenter_resource_context()

        self.assertRaises(Exception, self.deployer.deploy_from_template, self.si, deploy_from_template_details,
                          resource_context)
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
                    'auto_delete': 'True'
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

        res = self.deployer.deploy_from_image(self.si, session, vcenter_data_model, params, resource_context)

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
