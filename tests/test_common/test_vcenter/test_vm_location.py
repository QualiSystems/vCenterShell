import unittest
from common.vcenter.vm_location import VMLocation


class TestVmLocation(unittest.TestCase):
    def test_create_from_full_path(self):
        vm_location = VMLocation.create_from_full_path('QualiSB/Alex/test')

        self.assertEqual(vm_location.path, 'QualiSB/Alex')
        self.assertEqual(vm_location.name, 'test')

    def test_create_from_full_path_backslash(self):
        vm_location = VMLocation.create_from_full_path('QualiSB\\Alex\\test')

        self.assertEqual(vm_location.path, 'QualiSB/Alex')
        self.assertEqual(vm_location.name, 'test')
