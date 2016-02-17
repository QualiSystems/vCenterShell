import os
from driver_packager import pack_driver


class DriversPackager(object):

    @staticmethod
    def package_drivers(package_name):
        specs_dir = package_name + '_specs'

        if not os.path.exists(specs_dir):
            raise ValueError('Directory containing drivers''s specifications {0} does not exists.'.format(specs_dir))

        current_path = os.getcwd()
        spec_files = [os.path.join(current_path, specs_dir, f) for f in os.listdir(specs_dir) if f.endswith('.ini')]

        for spec_file in spec_files:
            pack_driver(spec_file)

