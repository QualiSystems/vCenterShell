import unittest
from common.utilites.common_utils import get_object_as_string


class TestCommonUtils(unittest.TestCase):
    def test_get_object_as_string_list(self):

        result = get_object_as_string(['value'])

        self.assertEqual(result, 'value')

    def test_get_object_as_string_string(self):

        result = get_object_as_string('value')

        self.assertEqual(result, 'value')
