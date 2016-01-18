import os
import sys
import zipfile
import ConfigParser

DRIVER_FILE_BASE_DIR = 'vCenterShellPackage'
STRIPING_CHARS = ' \t\n\r'
DRIVER_FOLDER = 'driver_folder'
INCLUDE_DIRS = 'include_dirs'
TARGET_NAME = 'target_name'
VERSION_FILENAME = 'version.txt'
TARGET_DIR = 'target_dir'


def zip_dir(path, zip_handler, include_dir=True):
    """
    zip all files and items in dir
    :param path:
    :param zip_handler: zip file handler
    :param boolean include_dir: specify if we want the archive with or without the directory
    """
    for root, dirs, files in os.walk(path):
        for file_to_zip in files:
            filename = os.path.join(root, file_to_zip)
            if os.path.isfile(filename):  # regular files only
                if include_dir:
                    zip_handler.write(filename)
                else:
                    zip_handler.write(filename, filename.split('\\', 1)[1])


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


def add_version_file_to_zip(ziph, driver_path=None):
    if not os.path.exists(VERSION_FILENAME):
        raise Exception('no version file found')
    ziph.write(VERSION_FILENAME)


def main(args):
    config_file_name = args[1]

    config = ConfigParser.ConfigParser()
    config.readfp(open(config_file_name))

    driver = config.get('Packaging', DRIVER_FOLDER)
    include_dirs = config.get('Packaging', INCLUDE_DIRS).split(',')
    target_name = config.get('Packaging', TARGET_NAME)
    target_dir = config.get('Packaging', TARGET_DIR)

    zip_name = os.path.join(DRIVER_FILE_BASE_DIR, target_dir, target_name + '.zip')

    print 'Packing driver {0} into {1}'.format(target_name, zip_name)

    ensure_dir(zip_name)

    # deletes old package
    if os.path.isfile(zip_name):
        os.remove(zip_name)

    zip_file = zipfile.ZipFile(zip_name, 'w')

    os.chdir(os.path.join(os.getcwd(), driver))
    zip_dir('.', zip_file)
    os.chdir(os.path.join(os.getcwd(), '../'))

    if driver.find("\\") != -1:
        path_parts = len(driver.split("\\")) - 1
        if path_parts > 0:
            path_fixer = ''
            for i in range(path_parts):
                path_fixer += '../'
            os.chdir(os.path.join(os.getcwd(), path_fixer))

    add_version_file_to_zip(zip_file)

    for dir_to_include in include_dirs:
        zip_dir(dir_to_include, zip_file)

    zip_file.close()

if __name__ == "__main__":
    main(sys.argv)
