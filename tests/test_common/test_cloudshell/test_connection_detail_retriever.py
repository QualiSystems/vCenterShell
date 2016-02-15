from unittest import TestCase

from mock import Mock

from common.cloud_shell.conn_details_retriever import ResourceConnectionDetailsRetriever


class TestConnectionDetailRetriever(TestCase):
    def test_connection_detail_retriever(self):
        helpers = Mock()
        cs_retriever_service = Mock()
        session = Mock()
        resource_context = Mock()
        connection_details = Mock()

        helpers.get_resource_context_details = Mock(return_value=resource_context)
        helpers.get_api_session = Mock(return_value=session)
        cs_retriever_service.getVCenterConnectionDetails = Mock(return_value=connection_details)
        retriever = ResourceConnectionDetailsRetriever(helpers, cs_retriever_service)

        res = retriever.connection_details()

        self.assertEqual(res, connection_details)
        self.assertTrue(helpers.get_resource_context_details.called)
        self.assertTrue(helpers.get_api_session.called)
        self.assertTrue(cs_retriever_service.getVCenterConnectionDetails.called_with(session, resource_context))
