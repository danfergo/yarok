import importlib
import os
from os import path
import os
import argparse

from .__init__ import run

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

        yarok run Environment Behaviour Arguments
            ->  yarok.run(Environmnet,Behaviour, **Arguments)

    """

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['run'])
    parser.add_argument('component', type=str)

    # parser.add_argument('-C', '--config-file', default='config.yaml',
    #                     help='Configuration file path (default: configs.xml)')
    # parser.add_argument('-O', '--output-format', default=None,
    #                     help='Output format produced: NetCDF4, HDF5, metainfo,...')
    # parser.add_argument('-I', '--input-format', default=None,
    #                     help='Input files format as produced by the Lidar: S100, V1,...')
    # parser.add_argument('-D', '--input-path', default=None,
    #                     help='Input datasets directory path')
    # parser.add_argument('-v', '--verbose', action='store_true', default=False,
    #                     help='explain what is being done')
    parser.add_argument('-V', '--version', action='store_true', default=False,
                        help='display version information and exit')
    # parser.add_argument('--debug', action='store_true', default=False,
    #                     help='Shows internal error messages')
    # parser.add_argument('--context', default='',
    #                     help='Path to which relative paths, such as config-file or data-path, are resolved.')

    args = parser.parse_args()

    # Logger.set_args(args)
    # Logger.header()

    if not args.version:
        # opts = parser.parse_args()
        # args_dict = vars(args)
        # args_dict.pop('verbose')
        # args_dict.pop('version')
        # args_dict.pop('debug')

        # print('XXXXXXXXXXXXXXXXXXXx', args.command)
        # dir_path = os.path.dirname(os.path.realpath(__file__))

        run(load(args.component), {
            'platform_args': {
                'viewer_mode': 'view'
            }
        })

        # builder = Builder(**args_dict)
        # builder.build()

    else:
        print('version 0.0.1')
        # Logger.log('about')
