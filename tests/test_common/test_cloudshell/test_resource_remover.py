from unittest import TestCase

from mock import Mock

from cloudshell.cp.vcenter.common.cloud_shell.resource_remover import CloudshellResourceRemover


class TestResourceRemover(TestCase):
    def test_resource_remover(self):
        # assert
        helpers = Mock()
        session = Mock()
        to_remove = 'remove this'

        session.DeleteResource = Mock(return_value=True)
        session = Mock(return_value=session)
        resource_remmover = CloudshellResourceRemover()

        # act
        resource_remmover.remove_resource(session, to_remove)

        # assert
        self.assertTrue(session.DeleteResource.called_with(to_remove))
