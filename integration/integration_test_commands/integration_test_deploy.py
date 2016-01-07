from unittest import TestCase

from mock import Mock
from pyVim.connect import SmartConnect, Disconnect

from common.utilites.common_name import generate_unique_name
from common.vcenter.vmomi_service import pyVmomiService
from models.DeployDataHolder import DeployDataHolder
from tests.utils.testing_credentials import TestCredentials
from vCenterShell.commands.deploy_vm import DeployFromTemplateCommand
from vCenterShell.vm.deploy import VirtualMachineDeployer


class VirtualMachinePowerManagementCommandIntegrationTest(TestCase):
    def test_deploy_template(self):
        # arrange
        resource_creator = Mock()

        cred = TestCredentials()
        pv_service = pyVmomiService(SmartConnect, Disconnect)
        si = pv_service.connect(cred.host, cred.username, cred.password)
        deployer = VirtualMachineDeployer(pv_service, generate_unique_name)

        # vm = pv_service.find_vm_by_name(si, 'QualiSB/Raz', '2')

        deploy_params = DeployDataHolder({
            "template_model": {
                "vCenter_resource_name": "QualiSB",
                "vm_folder": "QualiSB/Raz",
                "template_name": "a1"
            },
            "vm_cluster_model": {
                "cluster_name": "QualiSB Cluster",
                "resource_pool": "IT"
            },
            "datastore_name": "eric ds cluster",
            "power_on": False
        })

        deploy_command = DeployFromTemplateCommand(deployer, resource_creator)

        # act
        result = deploy_command.execute_deploy_from_template(si, deploy_params)

        # assert
        self.assertIsNotNone(result)
