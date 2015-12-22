import os.path
import sys
import json
import unittest
from mock import Mock, create_autospec
import jsonpickle
from vCenterShell.models.VCenterConnectionDetails import VCenterConnectionDetails
from vCenterShell.commands.DeployFromTemplateCommand import *
from pyVmomi import vim
from vCenterShell.models.VCenterTemplateModel import VCenterTemplateModel
from vCenterShell.models.VMClusterModel import VMClusterModel
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

    def test_serialize_and_deserialize_DataHolder_to_json(self):
        vcenter_template = VCenterTemplateModel("vCenter", "QualiSB/alex", "test")
        cluster_model = VMClusterModel("QualiSB Cluster", "LiverPool")
        data_holder = DataHolder.createFromParams(None, None, vcenter_template,"eric ds cluster", cluster_model, True)

        json_string = jsonpickle.encode(data_holder)

        print json_string

        decoded_data_holder = jsonpickle.decode(json_string)

        self.assertEquals(decoded_data_holder.resource_context, None)
        self.assertEquals(decoded_data_holder.connection_details, None)
        self.assertEquals(decoded_data_holder.power_on, True)
        self.assertEquals(decoded_data_holder.datastore_name, "eric ds cluster")
        self.assertEquals(decoded_data_holder.template_model.vCenter_resource_name, "vCenter")
        self.assertEquals(decoded_data_holder.template_model.vm_folder, "QualiSB/alex")
        self.assertEquals(decoded_data_holder.template_model.template_name, "test")
        self.assertEquals(decoded_data_holder.vm_cluster_model.cluster_name, "QualiSB Cluster")
        self.assertEquals(decoded_data_holder.vm_cluster_model.resource_pool, "LiverPool")


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
        command.deploy_execute()

        self.assertTrue(pvService.clone_vm.called)
        self.assertTrue(command.get_params_from_env.called)

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
        command.deploy_execute()

        # assert
        self.assertTrue(pvService.clone_vm.called)
        self.assertTrue(resource_connection_details_retriever.connection_details.called)
        self.assertTrue(command.get_params_from_env.called)
