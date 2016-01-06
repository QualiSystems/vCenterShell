# -*- coding: utf-8 -*-

import pprint
import sys


def nice_format(data):
    return pprint.pformat(data, indent=4)


def nice_print(data):
    print pprint.pformat(data, indent=4)


def print_attributes(obj, skip_private=True):
    for attr_name in dir(obj):
        if skip_private and attr_name.startswith("_"):
            continue
        try:
            print u"{:>20}: {}".format(attr_name, getattr(obj, attr_name))
        except:
            pass
