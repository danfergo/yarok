from .components_manager import ComponentsManager
from .inspector import Inspector
from .mjc.platform import PlatformMJC
from .hw.platform import PlatformHW

from .config import ConfigBlock

import inspect

import cv2
import time

__PLATFORM__ = None
__INSPECTOR__ = None
__CONFIG__ = None
__ENV_CONFIG__ = None


def get(config, key, default):
    return config[key] if key in config else default


def wait(fn=None, cb=None):
    global __PLATFORM__, __INSPECTOR__, __CONFIG__

    while True:
        __PLATFORM__.step()
        if __INSPECTOR__ is not None:
            __INSPECTOR__.probe()
        if __CONFIG__ is not None and 'callbacks' in __CONFIG__:
            [cb(__PLATFORM__) for cb in __CONFIG__['callbacks']]
        if fn is not None and fn():
            # cv2.waitKey(1)
            # time.sleep(0.0001)
            break
        if cb is not None:
            cb()
        # cv2.waitKey(1)
        # time.sleep(0.0001)

def wait_seconds(seconds, cb=None):
    start_seconds = time.time()
    wait(lambda: time.time() - start_seconds > seconds, cb)

def wait_forever(cb=None):
    wait(lambda: False, cb)

def load(config: {}):
    global __PLATFORM__, __INSPECTOR__, __CONFIG__, __ENV_CONFIG__

    config = ConfigBlock(config)
    config.defaults({
        'defaults': {
            'environment': 'sim'
        },
        'environments': {}
    })

    world = config['world']
    env = config['defaults']['environment']
    env_config = config['environments'][env]
    env_config.defaults(config['defaults'] if 'defaults' in config else {})

    manager = ComponentsManager(
        world,
        env_config['components']
    )

    platform_class = env_config['platform']['class'] \
        if env_config.is_config_block('platform') else env_config['platform']

    platform = platform_class(manager, env_config)

    __PLATFORM__ = platform
    __CONFIG__ = config
    __ENV_CONFIG__ = env_config
    if env_config['inspector']:
        __INSPECTOR__ = Inspector(manager, platform)

    return platform, manager


def run(config={}):
    platform, manager = load(config)

    behaviour = config['behaviour']

    if behaviour is not None:
        def get_component(c):
            if c == 'world':
                return manager.components_tree['instance']
            elif c == 'config':
                return __ENV_CONFIG__['behaviour']
            else:
                return manager.get_by_name(manager.components_tree, c)['instance']

        class_members = {t[0]: t[1] for t in inspect.getmembers(behaviour)}
        init_members = {t[0]: t[1] for t in inspect.getmembers(class_members['__init__'])}
        init_annotations = init_members['__annotations__'] if '__annotations__' in init_members else {}

        components = {c: get_component(c) for c in init_annotations}
        bh = behaviour(**components)
        if hasattr(bh, 'on_start'):
            bh.on_start()

        if hasattr(bh, 'on_update'):
            while True:
                if bh.on_update() == False:
                    break
                wait() # loops once.
