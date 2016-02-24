from types import FunctionType
from argparse import ArgumentParser
import inspect
import sys
from packaging.package_manager import PackageManager


def main():
    actions = get_actions()
    parser = ArgumentParser()
    parser.add_argument('action', type=str, help='Action to perform', choices=actions)

    # no arguments provided
    if len(sys.argv) == 1:
        # will display available actions
        parser.parse_args()
        return

    package_manager = PackageManager()
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action not in actions:
            raise ValueError('Action {0} is not supported'.format(action))
        method = getattr(package_manager, action)
        arguments = _get_method_arguments(method)
        for argument in arguments:
            parser.add_argument('--' + argument, type=str, required=True)
        args = parser.parse_args()
        method_params = [getattr(args, a) for a in dir(args) if a != 'action' and not a.startswith('_')]
        method(*method_params)


def _get_method_arguments(method):
    return [a for a in inspect.getargspec(method).args if a != 'self']


def get_actions():
    return [x for x, y in PackageManager.__dict__.items() if type(y) == FunctionType and not str(x).startswith('_')]


if __name__ == "__main__":
    main()
