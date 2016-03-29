from unittest import TestCase

from mock import Mock

from cloudshell.cp.vcenter.common.cloud_shell.conn_details_retriever import ResourceConnectionDetailsRetriever


class TestConnectionDetailRetriever(TestCase):
    def test_connection_detail_retriever(self):
        helpers = Mock()
        session = Mock()
        decrypted_password = Mock()
        decrypted_password.Value = 'decrypted password'
        session.DecryptPassword = Mock(return_value=decrypted_password)
        resource_context = Mock()
        resource_context.attributes = {'User': 'uzer', 'Password': 'password'}
        resource_context.address = '192.168.1.1'

        helpers.get_resource_context_details = Mock(return_value=resource_context)
        helpers.get_api_session = Mock(return_value=session)

        retriever = ResourceConnectionDetailsRetriever(helpers)

        connection_details = retriever.connection_details()

        self.assertEqual(connection_details.host, '192.168.1.1')
        self.assertEqual(connection_details.username, 'uzer')
        self.assertEqual(connection_details.password, 'decrypted password')
