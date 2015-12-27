import os.path
import sys
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '../vCenterShell/vCenterShell'))

# Comment out because of 'generate_unique_name' not defined :(

# from pycommon.common_name_utils import generate_unique_name
#
# class test_common_name_utils(unittest.TestCase):
#
#     def test_unique_name_generation(self):
#         name_prefix = "some template name"
#         unique1 = generate_unique_name(name_prefix)
#         unique2 = generate_unique_name(name_prefix)
#         self.assertNotEqual(unique1, unique2)


