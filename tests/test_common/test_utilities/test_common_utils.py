import unittest

from cloudshell.cp.vcenter.common.utilites.common_utils import get_object_as_string, str2bool


class TestCommonUtils(unittest.TestCase):
    def test_get_object_as_string_list(self):

        result = get_object_as_string(['value'])

        self.assertEqual(result, 'value')

    def test_get_object_as_string_string(self):

        result = get_object_as_string('value')

        self.assertEqual(result, 'value')

    def test_str2bool_True(self):
        result = str2bool(True)
        self.assertTrue(result)

    def test_str2bool_False(self):
        result = str2bool(False)
        self.assertFalse(result)

    def test_str2bool_True_as_string(self):
        result = str2bool('True')
        self.assertTrue(result)

    def test_str2bool_False_as_string(self):
        result = str2bool('False')
        self.assertFalse(result)

    def test_str2bool_unknown_error(self):
        self.assertRaises(Exception, str2bool, 'unknown')
