from xml.etree.ElementTree import tostring

from yarok.core.components_manager import ComponentsManager
from yarok.core.config_block import ConfigBlock
from yarok.core.platform import Platform


class PlatformHW(Platform):
    """
        Is the Platform for the Real World

    """

    def __init__(self, manager: ComponentsManager, config: ConfigBlock, behaviour):
        super(PlatformHW, self).__init__(manager, config, behaviour)
        self.interfaces = {
            id: self.manager.config(id)['interface_hw'](
                **{'config': config['interfaces'][c['name_path']] or ConfigBlock({})})
            for id, c in self.manager.components.items()
            if 'interface_hw' in self.manager.config(id)}

        self.init_components(self.interfaces)

        while not self.interfaces_ready():
            self.step()

    def interfaces_ready(self):
        return not (sum(
            [not self.interfaces[i].is_ready() for i in self.interfaces if hasattr(self.interfaces[i], 'step')]) > 0)

    def step(self):
        """
            Steps through all the interfaces
        """
        _ = {self.interfaces[i].step() for i in self.interfaces if hasattr(self.interfaces[i], 'step')}
