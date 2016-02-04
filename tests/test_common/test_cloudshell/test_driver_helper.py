from unittest import TestCase

from mock import Mock, patch, MagicMock
from qualipy.api.cloudshell_api import CloudShellAPISession

from common.cloudshell.driver_helper import CloudshellDriverHelper


class TestDriverHelper(TestCase):
    def setUp(self):
        self.helper = CloudshellDriverHelper()
        self.helper.cloudshell_data_retriever_service = Mock()
        self.helper.cloudshell_data_retriever_service.getVCenterConnectionDetails = Mock(return_value=True)
        self.helper.session_class = Mock()
        self.context = Mock()
        self.context.connectivity = Mock()
        self.context.connectivity.serverAddress = 'host'
        self.context.connectivity.adminAuthToken = 'token'
        self.context.reservation = Mock()
        self.context.reservation.domain = 'domain'

    def test_get_session(self):
        self.helper.get_session(self.context)
        self.assertTrue(self.helper.session_class.called_with(self.context.connectivity.serverAddress,
                                                              self.context.connectivity.adminAuthToken,
                                                              'admin',
                                                              'admin',
                                                              self.context.reservation.domain))

    def test_get_connection_details(self):
        session = Mock()
        res = self.helper.get_connection_details(session, self.context)
        self.assertTrue(res)
