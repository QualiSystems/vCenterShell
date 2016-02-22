from qualipy.api.QualiAPIClient import *
import argparse
import sys


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser = MyParser(argparse.ArgumentParser(description='QualiPackage builds and deploys the vCenterShell package to your Cloudshell server'))
parser.add_argument('--host', type=str, help='ip or hostname of Cloudshell server', default='localhost')
parser.add_argument('--port', type=int, help='Cloudshell server port for quali api requests (9000 by default)', default=9000)
parser.add_argument('--username', type=str, help='Admin username for Cloudshell Server', default='admin')
parser.add_argument('--password', type=str, help='Admin password for Cloudshell Server', default='admin')
parser.add_argument('--domain', type=str, help='Cloudshell domain, Global by default', default='Global')
parser.add_argument('--package', type=str, help='Package to upload', required=True)


args = parser.parse_args()

server = QualiAPIClient(args.host, args.port, args.username, args.password, args.domain)
server.upload_environment_zip_file(args.package)