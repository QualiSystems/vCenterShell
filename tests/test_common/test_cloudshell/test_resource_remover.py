from unittest import TestCase

from mock import Mock

from common.cloudshell.resource_remover import CloudshellResourceRemover


class TestResourceRemover(TestCase):
    def test_resource_remover(self):
        # assert
        helpers = Mock()
        session = Mock()
        to_remove = 'remove this'

        session.DeleteResource = Mock(return_value=True)
        helpers.get_api_session = Mock(return_value=session)
        resource_remmover = CloudshellResourceRemover(helpers)

        # act
        resource_remmover.remove_resource(to_remove)

        # assert
        self.assertTrue(helpers.get_api_session.called)
        self.assertTrue(session.DeleteResource.called_with(to_remove))
