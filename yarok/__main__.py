import importlib
import os
from os import path
import argparse

from .__init__ import run


def load(path, name):
    """
    Dynamically loads a module with name "name" and retrieves
    the class with the same name declared in that file.
    :param path:
    :param name:
    :return: loaded class.
    """
    print('---------_> ', __package__)
    return getattr(importlib.import_module(path, __package__), name)

def main():
    """
        Converter command entry point.
    """

    parser = argparse.ArgumentParser()

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
        # args_dict = vars(args)
        # args_dict.pop('verbose')
        # args_dict.pop('version')
        # args_dict.pop('debug')

        dir_path = os.path.dirname(os.path.realpath(__file__))

        run(load('.worlds.empty_world.empty_world', 'EmptyWorld'), {
            'platform_args': {
                'viewer_mode': 'view'
            }
        })

        # builder = Builder(**args_dict)
        # builder.build()
    else:
        print('version 0.0.1')
        # Logger.log('about')