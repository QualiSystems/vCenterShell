import unittest

from cloudshell.cp.vcenter.common.utilites.common_name import generate_unique_name


class test_common_name_utils(unittest.TestCase):
    def test_unique_name_generation(self):
        name_prefix = "some template name"
        unique1 = generate_unique_name(name_prefix)
        unique2 = generate_unique_name(name_prefix)
        self.assertNotEqual(unique1, unique2)

    def test_unique_name_generation_with_reservation_id(self):
        # arrange
        name_prefix = "some template name"
        reservation_id = "bcba3fe8-f56a-4f90-91c7-4262526f8ba5"

        # act
        unique1 = generate_unique_name(name_prefix, reservation_id)
        unique2 = generate_unique_name(name_prefix, reservation_id)

        # assert
        self.assertNotEqual(unique1, unique2)
        self.assertTrue(str(unique1).endswith("-8ba5"))
        self.assertTrue(str(unique2).endswith("-8ba5"))

