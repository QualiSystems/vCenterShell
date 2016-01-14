from unittest import TestCase
from mock import Mock
from vCenterShell.network.vnic.vnic_updater import VnicUpdater
from pyVmomi import vim


class TestVnicUpdater(TestCase):
    def test_update_vnics(self):

        # Arrange
        helpers = Mock()
        vnic_updater = VnicUpdater(helpers)

        # Act
        vnic_updater.update_vnics([(vim.vm.device.VirtualEthernetCard(), Mock(), Mock())], "VM1")

        # Assert
        self.assertTrue(helpers.SetConnectorAttributes.called)
