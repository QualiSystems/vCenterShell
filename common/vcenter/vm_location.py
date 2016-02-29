import re


class VMLocation(object):
    FORWARD_SLASH = '/'

    def __init__(self, path, name):
        self.path = path
        self.name = name

    @staticmethod
    def create_from_full_path(full_path):
        path_parts = re.split('/|\\\\', full_path)
        path = VMLocation.FORWARD_SLASH.join(path_parts[0:-1])
        name = path_parts[-1]
        return VMLocation(path=path, name=name)
