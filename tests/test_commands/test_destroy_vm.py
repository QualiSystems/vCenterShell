from vCenterShell.commands.destroy_vm import DestroyVirtualMachineCommand

__author__ = 'shms'

import os.path
import sys
import unittest
from mock import Mock, create_autospec
from pyVmomi import vim

sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))


class test_destroyVirtualMachineCommand(unittest.TestCase):
    def test_destroyVirtualMachineCommand(self):
        # arrange
        pv_service = Mock()
        resource_remover = Mock()
        disconnector = Mock()
        si = create_autospec(spec=vim.ServiceInstance)
        resource_name = 'this/is the name of the template'
        uuid = 'uuid'
        vm = Mock()

        pv_service.destory_mv = Mock(return_value=True)
        disconnector.remove_interfaces_from_vm = Mock(return_value=True)
        resource_remover.remove_resource = Mock(return_value=True)
        pv_service.find_by_uuid = Mock(return_value=vm)

        session = Mock()
        destroyer = DestroyVirtualMachineCommand(pv_service, resource_remover, disconnector)

        # act
        res = destroyer.destroy(si, session, uuid, resource_name)

        # assert
        self.assertTrue(res)
        self.assertTrue(pv_service.destory_mv.called_with(vm))
        self.assertTrue(disconnector.remove_interfaces_from_vm.called_with(si, vm))
        self.assertTrue(resource_remover.remove_resource.called_with(resource_name))
        self.assertTrue(pv_service.find_by_uuid.called_with(si, uuid))
