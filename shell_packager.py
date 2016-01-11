import os
import sys
import zipfile
from driver_packager import zip_dir, add_version_file_to_zip


def get_package_dir_name(package_name):
    package_name += "Package"
    if not os.path.exists(package_name):
        raise Exception('package folder "{0}" not found'.format(package_name))
    return package_name


def main(args):
    package_name = 'vCenterShell' #args[1]
    print "Building {0} package".format(package_name)

    zip_file = zipfile.ZipFile(package_name + ".zip", 'w')

    package_full_name = get_package_dir_name(package_name)
    zip_dir(package_full_name, zip_file, False)

    add_version_file_to_zip(zip_file)

    zip_file.close()
    print 'done!'


if __name__ == "__main__":
    main(sys.argv)
