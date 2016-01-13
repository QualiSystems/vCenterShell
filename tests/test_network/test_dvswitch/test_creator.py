from unittest import TestCase
from mock import Mock

from pyVmomi import vim
from vCenterShell.network.dvswitch.creator import DvPortGroupCreator


class TestDvPortGroupCreator(TestCase):

    def test_create_dv_port_group(self):
        # Arrange
        pyvmomy_service = Mock()
        pyvmomy_service.find_network_by_name = Mock(return_value=None)
        synchronous_task_waiter = Mock()

        # Act
        dv_port_group_creator = DvPortGroupCreator(pyvmomy_service, synchronous_task_waiter)

        # Assert
        self.assertRaises(Exception,
                          dv_port_group_creator.create_dv_port_group, 'port_name', 'switch_name', 'switch_path', Mock(),
                          None, None)

        dv_switch = Mock()
        spec = Mock(spec=vim.dvs.VmwareDistributedVirtualSwitch.VlanSpec)
        vlan_id = "111-33"
        res = DvPortGroupCreator.dv_port_group_create_task("TestGroup", dv_switch, spec, vlan_id)
        self.assertIsNotNone(res)