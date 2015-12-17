__author__ = 'shms'

import os.path
import sys
import unittest
from mock import Mock, create_autospec, MagicMock
import qualipy.scripts.cloudshell_scripts_helpers as helpers
from vCenterShell.commands.destroyVirtualMachineCommand import DestroyVirtualMachineCommand
from pyVmomi import vim
from vCenterShell.models.VCenterTemplateModel import VCenterTemplateModel
from vCenterShell.models.VMClusterModel import VMClusterModel
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))


class test_destroyVirtualMachineCommand(unittest.TestCase):

    def test_destroyVirtualMachineCommand(self):
        content = Mock()
        si = create_autospec(spec=vim.ServiceInstance)
        si.RetrieveContent = Mock(return_value=content)

        pvService = Mock()
        pvService.connect = Mock(return_value=si)
        pvService.destroy_vm_by_name = MagicMock()

        csRetrieverService = Mock()
        csRetrieverService.getVCenterTemplateAttributeData = Mock(return_value=VCenterTemplateModel(template_name='test', vm_folder='Alex', vCenter_resource_name='vCenter'))
        csRetrieverService.getPowerStateAttributeData = Mock(return_value=True)
        csRetrieverService.getVMClusterAttributeData = Mock(return_value=VMClusterModel(cluster_name="cluster1", resource_pool="resourcePool1"))
        csRetrieverService.getVMStorageAttributeData = Mock(return_value="datastore")
        csRetrieverService.getVCenterConnectionDetails = Mock(return_value={"vCenter_url": "vCenter","user":"user1","password":"pass1"})

        resource_att = Mock()
        vm_name = Mock(return_value='test')
        resource_att.name = vm_name
        helpers.get_resource_context_details = Mock(return_value=resource_att)
        helpers.get_api_session = Mock()

        command = DestroyVirtualMachineCommand(pvService, csRetrieverService)
        command.execute()

        self.assertTrue(pvService.connect.called)
        self.assertTrue(pvService.destroy_vm_by_name.called)
        self.assertTrue(si.RetrieveContent.called)
        pvService.destroy_vm_by_name.assert_called_with(content, si, vm_name)
        self.assertTrue(helpers.get_api_session().DeleteResource.called)

