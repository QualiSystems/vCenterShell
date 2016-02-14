from shell_publisher import ShellPublisher
from shell_packager import ShellPackager


class PackageManager(object):
    def __init__(self):
        pass

    def pack(self, package_name):
        packager = ShellPackager()
        packager.create_shell_package(package_name)

    def publish(self, package_name):
        packager = ShellPublisher()
        packager.publish(package_name)



