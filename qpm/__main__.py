from argparse import ArgumentParser
from packaging.package_manager import PackageManager
import pydevd
pydevd.settrace('127.0.0.1', port=51234, stdoutToServer=True, stderrToServer=True)


def main():

    parser = ArgumentParser()
    parser.add_argument('action', type=str, help='Action to perform: pack, publish, install')
    parser.add_argument('package', type=str, help='Package name')
    args = parser.parse_args()
    package_manager = PackageManager()
    if not hasattr(package_manager, args.action):
        raise ValueError('Action {0} is not supported'.format(args.action))
    method = getattr(package_manager, args.action)
    method(args.package)

if __name__ == "__main__":
    main()
