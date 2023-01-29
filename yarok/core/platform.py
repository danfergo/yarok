from abc import ABC, abstractmethod
from .components_manager import ComponentsManager
from .config_block import ConfigBlock
from .injector import Injector
import inspect

import time


class Platform(ABC):

    def __init__(self, manager, env_config, behaviour):
        self.manager = manager
        self.env_config = env_config
        self.behaviour = behaviour
        self.config = env_config['platform'] if 'platform' in env_config else ConfigBlock({})

        self.injector = Injector(self, self.manager.components_tree)
        self.plugins = [self.init_plugin(pl_tuple) for pl_tuple in env_config['plugins']]

    def init_plugin(self, plugin_tuple):

        if callable(plugin_tuple):
            return plugin_tuple

        plugin_cls = plugin_tuple[0] if type(plugin_tuple) is tuple else plugin_tuple
        plugin_conf = ConfigBlock(plugin_tuple[1] if type(plugin_tuple) is tuple else {})

        injector = Injector(self, self.manager.components_tree, plugin_conf)
        class_members = {t[0]: t[1] for t in inspect.getmembers(plugin_cls)}
        init_members = {t[0]: t[1] for t in inspect.getmembers(class_members['__init__'])}
        init_annotations = init_members['__annotations__'] if '__annotations__' in init_members else {}

        return plugin_cls(**injector.get_all(init_annotations))

    @staticmethod
    def create(config: ConfigBlock):

        from ..platforms.mjc.platform import PlatformMJC

        config = ConfigBlock(config)
        config.defaults({
            'defaults': {
                'environment': 'sim',
                'behaviour': {

                },
                'plugins': [

                ]
            },
            'environments': {
                'sim': {
                    'platform': {
                        'class': PlatformMJC
                    },
                    'components': {

                    }
                }
            }
        })

        world = config['world']
        behaviour = config['behaviour']
        env = config['defaults']['environment']
        env_config = config['environments'][env]
        env_config.defaults(config['defaults'] if 'defaults' in config else {})

        manager = ComponentsManager(
            world,
            env_config['components']
        )

        platform_class = env_config['platform']['class'] \
            if env_config.is_config_block('platform') else env_config['platform']
        return platform_class(manager, env_config, behaviour)

    @abstractmethod
    def step(self):
        pass

    def root(self):
        return self.manager.components_tree['instance']

    def init_components(self, interfaces):
        """
            Initializes components.
            Called after all the interfaces are instantiated (by the platform manager)

            Iterates through all components,
                - Gets the component class annotations,
                instantiates the component and stores at component['instance']

                - Gets and stores the component interface
        """

        def step_components(comp):
            # build the children, its dependencies, first.
            for child in comp['children']:
                step_components(child)

            c_data = comp['class'].__data__
            try:
                comp['injector'] = injector = Injector(self, comp)
                comp['instance'] = c = comp['class'](**{
                    n: injector.get(n, c_data['annotations'][n]) for n in c_data['annotations']
                })

                if comp['id'] in interfaces:
                    interface = c_data['interface_instance'] = interfaces[comp['id']]
                    methods = [i for i in dir(interface.__class__) if i[0:2] != '__']
                    [setattr(c, m, getattr(interface, m)) for m in methods if hasattr(c, m)]

            except TypeError as e:
                raise TypeError(str(e) + ', while initiating ' + str(comp['class']) + (
                    '/' + comp['name'] if comp['name'] is not None else ''))

        step_components(self.manager.components_tree)

    def run(self):

        if self.behaviour is not None:
            class_members = {t[0]: t[1] for t in inspect.getmembers(self.behaviour)}
            init_members = {t[0]: t[1] for t in inspect.getmembers(class_members['__init__'])}
            init_annotations = init_members['__annotations__'] if '__annotations__' in init_members else {}

            bh_config = self.env_config['behaviour']
            bh_injector = Injector(self, self.manager.components_tree, config=bh_config)
            bh = self.behaviour(**bh_injector.get_all(init_annotations))
            if hasattr(bh, 'on_start'):
                bh.on_start()

            if hasattr(bh, 'on_update'):
                while True:
                    if bh.on_update() == False:
                        break
                    self.wait_once()
        else:
            self.wait_forever()

    def wait(self, fn=None, cb=None):
        while True:
            self.step()
            if self.plugins:
                [(plugin() if callable(plugin) else plugin.step()) for plugin in self.plugins]
            if (fn is None) \
                    or (isinstance(fn, list) and not any([not e() for e in fn])) \
                    or (callable(fn) and fn()):
                break
            if cb is not None:
                cb()

    def wait_seconds(self, seconds, cb=None):
        start_seconds = time.time()
        self.wait(lambda: time.time() - start_seconds > seconds, cb)

    def wait_forever(self, cb=None):
        self.wait(lambda: False, cb)

    def wait_once(self, cb=None):
        self.wait(None, cb)
