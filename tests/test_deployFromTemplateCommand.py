import unittest
from mock import Mock, MagicMock, create_autospec, mock_open, patch
import sys
import os.path

from vCenterShell.models.VCenterConnectionDetails import VCenterConnectionDetails
from vCenterShell.models.VCenterTemplateModel import VCenterTemplateModel
from vCenterShell.models.VMClusterModel import VMClusterModel
from vCenterShell.pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))
from vCenterShell.commands.DeployFromTemplateCommand import *
from pyVmomi import vim

class test_deployFromTemplateCommand(unittest.TestCase):

    def test_deployFromTemplateCommand(self):
        content = Mock()
        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock(return_value=content)

        vmTemplate = Mock()

        pvService = Mock()
        pvService.connect = Mock(return_value=si)
        pvService.get_obj = Mock(return_value=vmTemplate)
        pvService.clone_vm = Mock()

        csRetrieverService = Mock()
        csRetrieverService.getVCenterTemplateAttributeData = Mock(return_value=VCenterTemplateModel(template_name='test', vm_folder='Alex', vCenter_resource_name='vCenter'))
        csRetrieverService.getPowerStateAttributeData = Mock(return_value=True)
        csRetrieverService.getVMClusterAttributeData = Mock(return_value=VMClusterModel(cluster_name="cluster1", resource_pool="resourcePool1"))
        csRetrieverService.getVMStorageAttributeData = Mock(return_value="datastore")
        csRetrieverService.getVCenterConnectionDetails = Mock(return_value={"vCenter_url": "vCenter","user":"user1","password":"pass1"})

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

