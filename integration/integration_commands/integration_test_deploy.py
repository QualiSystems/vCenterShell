from unittest import TestCase

from mock import Mock
from pyVim.connect import SmartConnect, Disconnect

from cloudshell.cp.vcenter.commands.deploy_vm import DeployCommand
from cloudshell.cp.vcenter.common.utilites.common_name import generate_unique_name
from cloudshell.cp.vcenter.common.vcenter.ovf_service import OvfImageDeployerService
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.models.DeployDataHolder import DeployDataHolder
from cloudshell.cp.vcenter.vm.deploy import VirtualMachineDeployer
from cloudshell.tests.utils.testing_credentials import TestCredentials


class VirtualMachinePowerManagementCommandIntegrationTest(TestCase):
    def test_deploy_template(self):
        # arrange

        cred = TestCredentials()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        si = pv_service.connect(cred.host, cred.username, cred.password)
        deployer = VirtualMachineDeployer(pv_service, generate_unique_name)

        # vm = pv_service.find_vm_by_name(si, 'QualiSB/Raz', '2')

        deploy_params = DeployDataHolder({
            "template_model": {
                "vCenter_resource_name": "QualiSB",
                "vm_folder": "QualiSB/Raz",
                "template_name": "2"
            },
            "vm_cluster_model": {
                "cluster_name": "QualiSB Cluster",
                "resource_pool": "IT"
            },
            "datastore_name": "eric ds cluster",
            "power_on": False
        })

        deploy_command = DeployCommand(deployer)

        # act
        result = deploy_command.execute_deploy_from_template(si, deploy_params)

        # assert
        self.assertIsNotNone(result)

    def test_deploy_image(self):
        # arrange

        cred = TestCredentials()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        si = pv_service.connect(cred.host, cred.username, cred.password)
        service = OvfImageDeployerService('C:\\Program Files\\VMware\\VMware OVF Tool\\ovftool.exe', Mock())
        deployer = VirtualMachineDeployer(pv_service, generate_unique_name, service)

        # vm = pv_service.find_vm_by_name(si, 'QualiSB/Raz', '2')

        params = DeployDataHolder(
            {
                "image_url": "http://192.168.65.88/ovf/Debian%2064%20-%20Yoav.ovf",
                "cluster_name": "QualiSB Cluster",
                "resource_pool": "LiverPool",
                "datastore_name": "datastore1",
                "datacenter_name": "QualiSB",
                "power_on": True,
                "app_name": "appName 1",
                "vm_folder": "Raz 2"
            })

        deploy_command = DeployCommand(deployer)
        # act
        result = deploy_command.execute_deploy_from_image(si, params, cred)

        # assert
        self.assertIsNotNone(result)
