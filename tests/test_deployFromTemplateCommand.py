import json
import unittest

from mock import Mock, create_autospec
from pyVmomi import vim
from models.VCenterConnectionDetails import VCenterConnectionDetails
from models.VCenterTemplateModel import VCenterTemplateModel

from models.VMClusterModel import VMClusterModel
from vCenterShell.commands.DeployFromTemplateCommand import *

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))


class test_deployFromTemplateCommand(unittest.TestCase):

    def test_deployFromTemplateCommand(self):
        content = Mock()
        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock(return_value=content)

        vmTemplate = Mock()

        pvService = Mock()
        pvService.connect = Mock(return_value=si)
        pvService.disconnect = Mock(return_value=Mock())
        pvService.get_obj = Mock(return_value=vmTemplate)
        cloned_vm = Mock()
        cloned_vm.error = None
        pvService.clone_vm = Mock(return_value=cloned_vm)

        csRetrieverService = Mock()
        csRetrieverService.getVCenterTemplateAttributeData = Mock(return_value=VCenterTemplateModel(template_name='test', vm_folder='Alex', vCenter_resource_name='vCenter'))
        csRetrieverService.getPowerStateAttributeData = Mock(return_value=True)
        csRetrieverService.getVMClusterAttributeData = Mock(return_value=VMClusterModel(cluster_name="cluster1", resource_pool="resourcePool1"))
        csRetrieverService.getVMStorageAttributeData = Mock(return_value="datastore")
        csRetrieverService.getVCenterConnectionDetails = Mock(return_value={"vCenter_url": "vCenter", "user":"user1", "password":"pass1"})

        resourceContext = Mock()
        resourceContext.attributes = {"vCenter Template": "vCenter/Alex/test"}
        helpers.get_resource_context_details = Mock(return_value=resourceContext)

        session = Mock()
        session.GetResourceDetails = Mock(return_value={})
        session.CreateResource = Mock()
        session.AddResourcesToReservation = Mock()
        session.SetAttributesValues = Mock()

        reservationContext = Mock(id="d8efb46f-4440-4685-b043-68de14ec4470")
        helpers.get_reservation_context_details = Mock(return_value=reservationContext)
        helpers.get_api_session = Mock(return_value=session)

        connection_details = VCenterConnectionDetails("vCenter", "user", "pass1")

        resource_connection_details_retriever = Mock()
        resource_connection_details_retriever.get_connection_details = Mock(return_value=connection_details)

        command = DeployFromTemplateCommand(pvService, csRetrieverService, resource_connection_details_retriever)
        command.execute()

        self.assertTrue(pvService.clone_vm.called)
        self.assertTrue(session.CreateResource.called)
        self.assertTrue(session.AddResourcesToReservation.called)
        self.assertTrue(session.SetAttributesValues.called)

    def test_deploy_execute_create_vm_error(self):
        content = Mock()
        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock(return_value=content)

        vmTemplate = Mock()

        pvService = Mock()
        pvService.connect = Mock(return_value=si)
        pvService.disconnect = Mock(return_value=Mock())
        pvService.get_obj = Mock(return_value=vmTemplate)
        cloned_vm = Mock()
        cloned_vm.error = 'this is mock error'

        pvService.clone_vm = Mock(return_value=cloned_vm)

        param = {
          "resource_context": None,
          "template_model": {
            "vCenter_resource_name": "vcenter_resource_name",
            "vm_folder": "vfolder_name",
            "template_name": "template_name"
          },
          "connection_details": {
            "host": "host",
            "username": "user",
            "password": "pass",
            "port": "port"
          },
          "vm_cluster_model": {
            "cluster_name": "cluster_name",
            "resource_pool": "resource_pool"
          },
          "datastore_name": "datastore_name",
          "power_on": False
        }

        command = DeployFromTemplateCommand(pvService, None, None)
        command.get_params_from_env = Mock(return_value=json.dumps(param))

        self.assertRaises(ValueError, command.execute_deploy_from_template)

        self.assertTrue(pvService.clone_vm.called)
        self.assertTrue(command.get_params_from_env.called)

    def test_deploy_execute_full_params(self):
        content = Mock()
        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock(return_value=content)

        vmTemplate = Mock()

        pvService = Mock()
        pvService.connect = Mock(return_value=si)
        pvService.disconnect = Mock(return_value=Mock())
        pvService.get_obj = Mock(return_value=vmTemplate)
        cloned_vm = Mock()
        cloned_vm.error = None
        cloned_vm.vm = Mock()
        cloned_vm.vm.summary = Mock()
        cloned_vm.vm.summary.config = Mock()
        cloned_vm.vm.summary.config.uuid = 'uuid_mock'

        pvService.clone_vm = Mock(return_value=cloned_vm)

        param = {
          "resource_context": None,
          "template_model": {
            "vCenter_resource_name": "vcenter_resource_name",
            "vm_folder": "vfolder_name",
            "template_name": "template_name"
          },
          "connection_details": {
            "host": "host",
            "username": "user",
            "password": "pass",
            "port": "port"
          },
          "vm_cluster_model": {
            "cluster_name": "cluster_name",
            "resource_pool": "resource_pool"
          },
          "datastore_name": "datastore_name",
          "power_on": False
        }

        command = DeployFromTemplateCommand(pvService, None, None)
        command.get_params_from_env = Mock(return_value=json.dumps(param))
        command.execute_deploy_from_template()

        self.assertTrue(pvService.clone_vm.called)
        self.assertTrue(command.get_params_from_env.called)

    def test_get_params_from_env(self):
        # arrange
        env_param = '{"this": "is json"}'
        os.environ.__setitem__('DEPLOY_DATA', env_param)
        command = DeployFromTemplateCommand(None, None, None)

        # act
        params = command.get_params_from_env()

        # assert
        self.assertEqual(params, env_param)

    def test_deploy_execute_no_connection_details(self):
        # set
        content = Mock()
        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock(return_value=content)

        vmTemplate = Mock()

        pvService = Mock()
        pvService.connect = Mock(return_value=si)
        pvService.disconnect = Mock(return_value=Mock())
        pvService.get_obj = Mock(return_value=vmTemplate)
        cloned_vm = Mock()
        cloned_vm.error = None
        cloned_vm.vm = Mock()
        cloned_vm.vm.summary = Mock()
        cloned_vm.vm.summary.config = Mock()
        cloned_vm.vm.summary.config.uuid = 'uuid_mock'

        pvService.clone_vm = Mock(return_value=cloned_vm)

        param = {
          "resource_context": None,
          "template_model": {
            "vCenter_resource_name": "vcenter_resource_name",
            "vm_folder": "vfolder_name",
            "template_name": "template_name"
          },
          "connection_details": None,
          "vm_cluster_model": {
            "cluster_name": "cluster_name",
            "resource_pool": "resource_pool"
          },
          "datastore_name": "datastore_name",
          "power_on": False
        }

        connection_details = VCenterConnectionDetails("vCenter", "user", "pass1")
        resource_connection_details_retriever = Mock()
        resource_connection_details_retriever.get_connection_details = Mock(return_value=connection_details)

        command = DeployFromTemplateCommand(pvService, None, resource_connection_details_retriever)
        command.get_params_from_env = Mock(return_value=json.dumps(param))

        # act
        command.execute_deploy_from_template()

        # assert
        self.assertTrue(pvService.clone_vm.called)
        self.assertTrue(resource_connection_details_retriever.connection_details.called)
        self.assertTrue(command.get_params_from_env.called)
