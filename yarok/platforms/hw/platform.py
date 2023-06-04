from xml.etree.ElementTree import tostring

from yarok.core.components_manager import ComponentsManager
from yarok.core.config_block import ConfigBlock
from yarok.core.platform import Platform
from yarok.core.injector import Injector

import inspect


class PlatformHW(Platform):
    """
        Is the Platform for the Real World

    """

    def __init__(self, manager: ComponentsManager, config: ConfigBlock, behaviour):
        super(PlatformHW, self).__init__(manager, config, behaviour)
        self.interfaces = {
            id: self.init_interface(id, config['interfaces'][c['name_path']] or ConfigBlock({}))
            for id, c in self.manager.components.items()
            if 'interface_hw' in self.manager.config(id)}

        self.init_components(self.interfaces)

        while not self.interfaces_ready():
            self.step()

    def init_interface(self, n, interface_runtime_config):
        x = self.manager.config(n)
        interface_cls = self.manager.config(n)['interface_hw']

        # backwards compatible:
        if not hasattr(self.manager.config(n)['interface_hw'], '__data__'):
            print('[deprecated] interfaces should be annotated with the @interface decorator')
            return interface_cls(interfaces_mjc[n])

        class_members = {t[0]: t[1] for t in inspect.getmembers(interface_cls)}
        init_members = {t[0]: t[1] for t in inspect.getmembers(class_members['__init__'])}
        init_annotations = init_members['__annotations__'] if '__annotations__' in init_members else {}

        interface_defaults = interface_cls.__data__['defaults']
        config = ConfigBlock(interface_runtime_config)
        config.defaults(interface_defaults)

        providers = [
            {'match_type': ConfigBlock, 'value': config},
        ]

        injector = Injector(self, providers=providers)

        return interface_cls(**injector.get_all(init_annotations))

    def interfaces_ready(self):
        return not (sum(
            [not self.interfaces[i].is_ready() for i in self.interfaces if hasattr(self.interfaces[i], 'step')]) > 0)

    def step(self):
        """
            Steps through all the interfaces
        """
        _ = {self.interfaces[i].step() for i in self.interfaces if hasattr(self.interfaces[i], 'step')}