from xml.etree.ElementTree import tostring

# from mujoco import MjSim, load_model_from_xml, MjRenderContextOffscreen

from ..components_manager import ComponentsManager
from ..config import ConfigBlock
from .viewer import ViewerHW


class PlatformHW:
    """
        Is the Platform for the MuJoCo simulator

        Manages the environment platform and necessary integrations.

        1. Starts MjSim with the manager.xml_tree
        2. Instantiates the interfaces for each MuJoCo sensor, actuator or camera.
        3. Instantiates the viewer (i.e. ViewerMJC)
        4. Instantiates the components

        Exposes the step() method that steps() through all the interfaces.
    """

    def __init__(self, manager: ComponentsManager, config: ConfigBlock):
        self.manager = manager
        self.interfaces = {
            id: self.manager.data(id)['interfaces']['hw'](
                **{'config': config['interfaces'][c['name_path']] or ConfigBlock({})})
            for id, c in self.manager.components.items()
            if 'hw' in self.manager.data(id)['interfaces']}

        manager.init_components(self.interfaces, config['components'])

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
        # self.viewer.step()
