from .components_manager import ComponentsManager
from .inspector import Inspector
from .mjc.platform import PlatformMJC

import inspect

__PLATFORM__ = None


def wait(fn):
    global __PLATFORM__

    while True:
        __PLATFORM__.step()
        if fn():
            break


def load(world, config):
    def get_config(key, default):
        return config[key] if key in config else default

    manager = ComponentsManager(
        root=world,
    )

    platform = get_config('plaform', PlatformMJC)(manager, **get_config('platform_args', {}))

    return platform, manager


def run(world, behaviour=None, config={}):
    global __PLATFORM__

    platform, manager = load(world, config)
    inspector = Inspector(manager)

    __PLATFORM__ = platform

    if behaviour is not None:
        class_members = {t[0]: t[1] for t in inspect.getmembers(behaviour)}
        init_members = {t[0]: t[1] for t in inspect.getmembers(class_members['__init__'])}
        init_annotations = init_members['__annotations__'] if '__annotations__' in init_members else {}

        components = {c: manager.get(c)['instance'] for c in init_annotations}

        bh = behaviour(**components)
        bh.wake_up()
    else:
        while True:
            platform.step()
            if not (config['platform_args'] and config['platform_args']['viewer_mode'] == 'view'):
                inspector.probe()
