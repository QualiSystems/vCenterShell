from unittest import TestCase
from common.utilites.command_result import get_result_from_command_output


class TestCommandResult(TestCase):

    def test_command_result_with_result(self):
        result = get_result_from_command_output('command_json_result=MY RESULT=command_json_result_end')
        self.assertEqual(result, 'MY RESULT')

    def test_command_result_empty(self):
        result = get_result_from_command_output('')
        self.assertEqual(result, None)
