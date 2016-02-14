from argparse import ArgumentParser
from packaging.package_manager import PackageManager


def main():

    parser = ArgumentParser()
    parser.add_argument('action',  type=str, help='Action to perform: pack, publish, install')
    parser.add_argument('package',  type=str, help='Package name')
    args = parser.parse_args()
    package_manager = PackageManager()
    print args.action + ' ' + args.package
    method = getattr(package_manager, args.action)
    method(args.package)

if __name__ == "__main__":
    main()
