import ConfigParser
import os
#from qualipy.api.QualiAPIClient import QualiAPIClient
from cloudshell.api.cloudshell_api import CloudShellAPISession
from qualipy.api.QualiAPIClient import QualiAPIClient


class ShellInstaller(object):
    def install(self, package_name):
        config = ConfigParser.ConfigParser()

        config_path = os.path.join(os.getcwd(), 'qpm.ini')
        config.readfp(open(config_path))
        host = config.get('Installation', 'host') or 'localhost'
        port = config.get('Installation', 'port') or '9000'
        username = config.get('Installation', 'username') or 'admin'
        password = config.get('Installation', 'password') or 'admin'
        domain = config.get('Installation', 'domain') or 'Global'

        server = QualiAPIClient(host, port, username, password, domain)
        server.upload_environment_zip_file(os.path.join(os.getcwd(), package_name + '.zip'))
