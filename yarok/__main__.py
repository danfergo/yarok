import importlib
import os
from os import path
import os
import argparse

from .__init__ import run, __VERSION__

import importlib.util
import sys
from enum import Enum


# adapted from https://stackoverflow.com/questions/19053707/converting-snake-case-to-lower-camel-case-lowercamelcase
def to_camel_case(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return ''.join(x.title() for x in components)


def load(p):
    """
    Dynamically loads a module with name "name" and retrieves
    the class with the same name declared in that file.
    :param p:
    :param class_name:
    :return: loaded class.
    """

    module_name = p[p.rfind('.') + 1:]

    try:
        spec = importlib.util.spec_from_file_location(module_name, os.getcwd() + '/' + p.replace('.', '/') + ".py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except FileNotFoundError:
        module = importlib.import_module('.components.' + p, __package__)
    return getattr(module, to_camel_case(module_name))


def main():
    """
        yarok cli entry point.
        Parses the cli arguments and calls the corresponding python methods/apis, e.g.,

        yarok run World
            ->  yarok.run(config)
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['run'])
    parser.add_argument('component', type=str)

    parser.add_argument('-V', '--version', action='store_true', default=False,
                        help='display version information and exit')

    args = parser.parse_args()

    if args.version:
        print('Version ' + __VERSION__)
    else:
        run({
            'world': load(args.component),
            'platform_args': {
                'viewer_mode': 'view'
            }
        })


if __name__ == '__main__':
    main()
