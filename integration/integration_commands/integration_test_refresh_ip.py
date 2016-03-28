from unittest import TestCase

from mock import Mock
from pyVim.connect import SmartConnect, Disconnect

from cloudshell.cp.vcenter.commands.refresh_ip import RefreshIpCommand
from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.models.VCenterConnectionDetails import VCenterConnectionDetails
from cloudshell.tests.utils.testing_credentials import TestCredentials
from cloudshell.tests.utils import helpers


class TestRefreshIpCommand(TestCase):
    def integrationtest_refresh_ip(self):
        resource_context = Mock()
        resource_context.attributes = {"vCenter Template": "vCenter/Alex/test"}
        qualipy_helpers = Mock()
        qualipy_helpers.get_resource_context_details = Mock(return_value=resource_context)

        credentials = TestCredentials()
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cloudshell_data_retriever_service = Mock()
        cloudshell_data_retriever_service.getVCenterConnectionDetails = Mock(
                return_value=VCenterConnectionDetails(credentials.host, credentials.username, credentials.password))

        vm_resource = Mock()
        vm_resource.default_network = 'default'

        resource_model_parser = Mock()
        resource_model_parser.convert_to_resource_model = Mock(return_value=vm_resource)

        refresh_ip_command = RefreshIpCommand(py_vmomi_service, cloudshell_data_retriever_service, qualipy_helpers,
                                              resource_model_parser)

        uuid = helpers.get_uuid('vCenter-Server-Appliance-yaniv')
        refresh_ip_command.refresh_ip(uuid, '')

        pass

    def test_integrationtest_refresh_ip(self):
        resource_context = Mock()
        resource_context.attributes = {"vCenter Template": "vCenter/Boris/Boris2-win7"}
        qualipy_helpers = Mock()
        qualipy_helpers.get_resource_context_details = Mock(return_value=resource_context)

        credentials = TestCredentials()
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        si = py_vmomi_service.connect(credentials.host, credentials.username, credentials.password)
        cloudshell_data_retriever_service = Mock()
        cloudshell_data_retriever_service.getVCenterConnectionDetails = Mock(
                return_value=VCenterConnectionDetails(credentials.host, credentials.username, credentials.password))

        vm_resource = Mock()
        vm_resource.default_network = 'default'

        resource_model_parser = Mock()
        resource_model_parser.convert_to_resource_model = Mock(return_value=vm_resource)

        refresh_ip_command = RefreshIpCommand(py_vmomi_service, cloudshell_data_retriever_service, qualipy_helpers,
                                              resource_model_parser)

        # uuid = helpers.get_uuid('VM Deployment_afee8038')
        ip = refresh_ip_command.refresh_ip(si, '4222f613-e714-6204-8095-e282796985fb', 'VM Deployment_afee8038')
        print ip
        pass

    def test_vm_ware_tools(self):
        credentials = TestCredentials()
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        si = py_vmomi_service.connect(credentials.host, credentials.username, credentials.password)
        vm = py_vmomi_service.get_vm_by_uuid(si, '4222f613-e714-6204-8095-e282796985fb')

        self.assertIsNotNone(vm.guest)

