from xml.etree.ElementTree import tostring

from mujoco_py import MjSim, load_model_from_xml

from ..components_manager import ComponentsManager
from ..mjc.interface import InterfaceMJC
from ..mjc.viewer import ViewerMJC

INTERFACES_COMPONENTS_NAMES = [
    'sensor',
    'actuator',
    'camera'
]


class PlatformMJC:
    """
        Is the Platform for the MuJoCo simulator

        Manages the environment platform and necessary integrations.

        1. Starts MjSim with the manager.xml_tree
        2. Instantiates the interfaces for each MuJoCo sensor, actuator or camera.
        3. Instantiates the viewer (i.e. ViewerMJC)
        4. Instantiates the components

        Exposes the step() method that steps() through all the interfaces.
    """

    def __init__(self, manager: ComponentsManager, viewer_mode='view'):
        self.model = load_model_from_xml(tostring(manager.xml_tree, encoding="unicode"))
        self.manager = manager
        self.sim = MjSim(self.model)

        interfaces_mjc = {n: InterfaceMJC(n, self.sim, self.model)
                          for n, c in self.manager.components.items()
                          if 'mjc' in self.manager.data(n)['interfaces']}

        self.init_mjc_interfaces(interfaces_mjc)
        self.interfaces = {n: self.manager.data(n)['interfaces']['mjc'](interfaces_mjc[n])
                           for n, interface_mjc in interfaces_mjc.items()}

        self.viewer = ViewerMJC(self.sim, viewer_mode)

        manager.init_components(self.interfaces)

    def init_mjc_interfaces(self, interfaces_mjc):
        """
            Instantiates interfaces for sensors, actuators, and cameras.
        """

        for item in INTERFACES_COMPONENTS_NAMES:
            for idx in range(len(getattr(self.model, item + '_names'))):
                abs_name = getattr(self.model, item + '_id2name')(idx)
                col_idx = abs_name.index(':')
                component_name = abs_name[:col_idx]
                item_name = abs_name[col_idx + 1:]

                if component_name in interfaces_mjc:
                    interface = interfaces_mjc[component_name]
                    getattr(interface, item + '_name2id')[item_name] = idx
                    getattr(interface, item + 's').append(item_name)
                    interface.component_name = component_name

    def step(self):
        """
            Steps through all the interfaces
        """
        self.sim.step()
        _ = {self.interfaces[i].step() for i in self.interfaces if hasattr(self.interfaces[i], 'step')}
        self.viewer.step()
