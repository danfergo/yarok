from .components_manager import ComponentsManager

from .mjc.platform import PlatformMJC


def run(world, config):
    def get_config(key, default):
        return config[key] if key in config else default

    manager = ComponentsManager(
        root=world,
    )

    platform = get_config('plaform', PlatformMJC)(manager, **get_config('platform_args', {}))

    manager.init_components(platform.interfaces)

    while True:
        platform.step()
