import os
import sys
import zipfile

DRIVER_FILE_NAME_FORMAT = 'vCenterShellPackage/Resource Scripts/{0}.zip'
STRIPING_CHARS = ' \t\n\r'
DRIVER_FOLDER = 'driver_folder'
INCLUDE_DIRS = 'include_dirs'
TARGET_NAME = 'target_name'
VERSION_FILENAME = 'version.txt'


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


def add_version_file_to_zip(ziph):
    if not os.path.exists(VERSION_FILENAME):
        raise Exception('no version file found')
    ziph.write(VERSION_FILENAME)


def main(args):
    config_file_name = args[1]
    #driver = args[2]
    #target_name = args[3]


    with open(config_file_name) as f_config:
        if f_config is None:
            raise Exception('no packager config file found')
        config = dict()
        config_raw = f_config.read().splitlines()
        for att in config_raw:
            cnf_att = att.split(':')
            config[cnf_att[0].strip(' \t\n\r')] = cnf_att[1].strip(STRIPING_CHARS).split(',')

    target_name = config[TARGET_NAME][0]
    driver = config[DRIVER_FOLDER][0]

    print 'packing driver: {0}'.format(target_name)

    zip_name = DRIVER_FILE_NAME_FORMAT.format(target_name)

    ensure_dir(zip_name)

    # deletes old package
    if os.path.isfile(zip_name):
        os.remove(zip_name)

    zip_file = zipfile.ZipFile(zip_name, 'w')

    os.chdir(os.path.join(os.getcwd(), driver))
    zip_dir('.', zip_file)
    os.chdir(os.path.join(os.getcwd(), '../'))

    add_version_file_to_zip(zip_file)

    for dir_to_include in config[INCLUDE_DIRS]:
        zip_dir(dir_to_include, zip_file)

    zip_file.close()

    print 'done!'


if __name__ == "__main__":
    main(sys.argv)
