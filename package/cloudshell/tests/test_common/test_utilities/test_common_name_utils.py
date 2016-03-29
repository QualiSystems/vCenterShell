import unittest

from cloudshell.cp.vcenter.common.utilites.common_name import generate_unique_name


class test_common_name_utils(unittest.TestCase):
    def test_unique_name_generation(self):
        name_prefix = "some template name"
        unique1 = generate_unique_name(name_prefix)
        unique2 = generate_unique_name(name_prefix)
        self.assertNotEqual(unique1, unique2)
