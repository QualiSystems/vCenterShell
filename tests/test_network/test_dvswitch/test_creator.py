from unittest import TestCase

from mock import Mock, create_autospec
from pyVmomi import vim
from vCenterShell.network.dvswitch.creator import DvPortGroupCreator


class TestDvPortGroupCreator(TestCase):
    def test_create_dv_port_group_exception(self):
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

    def test_create_dv_port_group(self):
        # Arrange

        dv_switch = create_autospec(spec=vim.DistributedVirtualSwitch)
        dv_switch.portgroup = Mock()
        pyvmomy_service = Mock()
        pyvmomy_service.find_network_by_name = Mock(return_value=dv_switch)
        synchronous_task_waiter = Mock()
        dv_port_group_creator = DvPortGroupCreator(pyvmomy_service, synchronous_task_waiter)
        DvPortGroupCreator.dv_port_group_create_task = Mock()

        # Act
        dv_port_group_creator.create_dv_port_group('port_name', 'switch_name', 'switch_path',
                                                   create_autospec(spec=vim.ServiceInstance), None, 1001)

        # Assert
        self.assertTrue(dv_port_group_creator.dv_port_group_create_task.called)

