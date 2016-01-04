from unittest import TestCase

from mock import Mock
from pycommon.wrappers.CommandWrapper import CommandWrapper


class TestCommandWrapper(TestCase):
    def setUp(self):
        self.si = Mock()
        self.logger = Mock()
        self.connection_detail = Mock()
        self.pv_service = Mock()
        self.pv_service.connect = Mock(return_value=self.si)
        self.connection_detail.host = 'host'
        self.connection_detail.username = 'user'
        self.connection_detail.password = 'password'
        self.connection_detail.port = 'port'

    def test_execute_command_with_params(self):
        # arrange
        def fake_command_with_connection_return_true(si, fake1, fake2):
            return True

        wrapper = CommandWrapper(self.logger, self.pv_service)

        # act
        res = wrapper.execute_command_with_connection(self.connection_detail,
                                                      fake_command_with_connection_return_true,
                                                      'param 1',
                                                      'param2')

        # assert
        self.assertTrue(res)

    def test_execute_command(self):
        # arrange
        def fake_command_with_connection_return_true(fake1, fake2):
            return True

        wrapper = CommandWrapper(self.logger, self.pv_service)

        # act
        res = wrapper.execute_command(fake_command_with_connection_return_true,
                                      'param 1',
                                      'param2')

        # assert
        self.assertTrue(res)

    def test_execute_command_no_command(self):
        # arrange
        wrapper = CommandWrapper(self.logger, self.pv_service)

        # assert
        self.assertRaises(Exception, wrapper.execute_command, None)

    def test_execute_command_no_args(self):
        # arrange
        wrapper = CommandWrapper(self.logger, self.pv_service)

        # assert
        self.assertRaises(Exception, wrapper.execute_command, None)

    def test_execute_command_no_logger(self):
        # arrange
        wrapper = CommandWrapper(None, self.pv_service)

        # assert
        self.assertRaises(Exception, wrapper.execute_command, None)

    def test_execute_command_no_logger(self):
        # arrange
        wrapper = CommandWrapper(None, self.pv_service)

        # assert
        self.assertRaises(Exception, wrapper.execute_command, None)