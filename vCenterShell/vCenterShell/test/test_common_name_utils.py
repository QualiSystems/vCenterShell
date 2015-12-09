import unittest
from pycommon.common_name_utils import generate_unique_name

class test_common_pyvmomi(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_unique_name_generation(self):
        name_prefix = "some template name"
        unique1 = generate_unique_name(name_prefix)
        unique2 = generate_unique_name(name_prefix)
        self.assertNotEqual(unique1, unique2)



if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)

