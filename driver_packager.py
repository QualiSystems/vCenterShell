import os
import sys
import zipfile

DRIVER_FILE_NAME_FORMAT = '{0}_{1}.zip'
STRIPING_CHARS = ' \t\n\r'
INCLUDE_DIRS = 'include_dirs'


def zip_dir(path, ziph):
    """
    zip all files and items in dir
    :param path:
    :param ziph:
    """
    for root, dirs, files in os.walk(path):
        for file_to_zip in files:
            filename = os.path.join(root, file_to_zip)
            if os.path.isfile(filename):  # regular files only
                ziph.write(filename)


args = sys.argv
drivers = args[2:]
confing_file_name = args[1]

print 'going to pack: {0}'.format(','.join(drivers))

with open('version.txt') as f_version:
    if f_version is None:
        raise Exception('no version file found')
    version = f_version.read()
    if not version:
        raise Exception('no version file found')

with open(confing_file_name) as f_config:
    if f_config is None:
        raise Exception('no packager config file found')
    confing = dict()
    config_raw = f_config.read().splitlines()
    for att in config_raw:
        cnf_att = att.split(':')
        confing[cnf_att[0].strip(' \t\n\r')] = cnf_att[1].strip(STRIPING_CHARS).split(',')


for driver in drivers:
    zip_name = DRIVER_FILE_NAME_FORMAT.format(driver, version)
    # deletes old package
    if os.path.isfile(zip_name):
        os.remove(zip_name)

    zip_file = zipfile.ZipFile(zip_name, 'w')

    os.chdir(os.path.join(os.getcwd(), driver))
    zip_dir('.', zip_file)
    os.chdir(os.path.join(os.getcwd(), '../'))

    for dir_to_include in confing[INCLUDE_DIRS]:
        zip_dir(dir_to_include, zip_file)

    zip_file.close()

print 'done!'
