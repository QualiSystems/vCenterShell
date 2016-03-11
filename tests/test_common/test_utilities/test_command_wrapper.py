from unittest import TestCase

from mock import Mock

from vCenterShell.common import CommandWrapper


class TestCommandWrapper(TestCase):
    def setUp(self):
        self.si = Mock()
        self.logger = Mock()
        self.pv_service = Mock()
        self.pv_service.connect = Mock(return_value=self.si)
        self.cloud_shell_helper = Mock()
        self.resource_model_parser = Mock()

    def test_execute_command_with_params_and_vcetner_data_model_with_session_inject(self):
        # arrange
        def fake_command_with_connection_return_true_1(si, vcenter_data_model, session, fake1, fake2):
            return True
        def fake_command_with_connection_return_true_2(si, session, vcenter_data_model, fake1, fake2):
            return True

        wrapper = CommandWrapper(self.logger, self.pv_service, self.cloud_shell_helper, self.resource_model_parser)
        context = Mock()

        # act
        res_1 = wrapper.execute_command_with_connection(context,
                                                      fake_command_with_connection_return_true_1,
                                                      'param 1',
                                                      'param2')
        res_2 = wrapper.execute_command_with_connection(context,
                                                      fake_command_with_connection_return_true_2,
                                                      'param 1',
                                                      'param2')
        # assert
        self.assertTrue(res_1)
        self.assertTrue(res_2)

    def test_execute_command_with_params_and_vcetner_data_model_inject(self):
        # arrange
        def fake_command_with_connection_return_true(si, vcenter_data_model, fake1, fake2):
            return True

        wrapper = CommandWrapper(self.logger, self.pv_service, self.cloud_shell_helper, self.resource_model_parser)
        context = Mock()

        # act
        res = wrapper.execute_command_with_connection(context,
                                                      fake_command_with_connection_return_true,
                                                      'param 1',
                                                      'param2')
        # assert
        self.assertTrue(res)

    def test_execute_command_with_params_and_session_inject(self):
        # arrange
        def fake_command_with_connection_return_true(si, session, fake1, fake2):
            return True

        wrapper = CommandWrapper(self.logger, self.pv_service, self.cloud_shell_helper, self.resource_model_parser)
        context = Mock()

        # act
        res = wrapper.execute_command_with_connection(context,
                                                      fake_command_with_connection_return_true,
                                                      'param 1',
                                                      'param2')
        # assert
        self.assertTrue(res)

    def test_execute_command_with_params(self):
        # arrange
        def fake_command_with_connection_return_true(si, fake1, fake2):
            return True

        wrapper = CommandWrapper(self.logger, self.pv_service, self.cloud_shell_helper, self.resource_model_parser)
        context = Mock()

        # act
        res = wrapper.execute_command_with_connection(context,
                                                      fake_command_with_connection_return_true,
                                                      'param 1',
                                                      'param2')
        # assert
        self.assertTrue(res)

    def test_execute_command(self):
        # arrange
        def fake_command_with_connection_return_true(fake1, fake2):
            return True

        wrapper = CommandWrapper(self.logger, self.pv_service, self.cloud_shell_helper, self.resource_model_parser)

        # act
        res = wrapper.execute_command(fake_command_with_connection_return_true,
                                      'param 1',
                                      'param2')

        # assert
        self.assertTrue(res)

    def test_execute_command_no_command(self):
        # arrange
        wrapper = CommandWrapper(self.logger, self.pv_service, self.cloud_shell_helper, self.resource_model_parser)

        # assert
        self.assertRaises(Exception, wrapper.execute_command, None)

    def test_execute_command_no_logger(self):
        # arrange
        wrapper = CommandWrapper(None, self.pv_service, self.cloud_shell_helper, self.resource_model_parser)

        # assert
        self.assertRaises(Exception, wrapper.execute_command, None)

    def test_execute_command_no_args(self):
        # arrange
        wrapper = CommandWrapper(self.logger, self.pv_service, self.cloud_shell_helper, self.resource_model_parser)

        # assert
        self.assertRaises(Exception, wrapper.execute_command, None)

    def test_execute_command_exception_in_command(self):
        # arrange
        def command():
            raise Exception('evil')
        wrapper = CommandWrapper(self.logger, self.pv_service, self.cloud_shell_helper, self.resource_model_parser)

        # assert
        self.assertRaises(Exception, wrapper.execute_command, command)