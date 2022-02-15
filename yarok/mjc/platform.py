from xml.etree.ElementTree import tostring

from mujoco_py import MjSim, load_model_from_xml

from ..components_manager import ComponentsManager
from ..mjc.interface import InterfaceMJC
from ..mjc.viewer import ViewerMJC


class PlatformMJC:
    """
        Manages the environment platform and necessary ports.
        Instantiates the corresponding interfaces.

        Manages the Mujoco Simulation Environment
    """

    def __init__(self, manager: ComponentsManager, viewer_mode='view'):
        xml = tostring(manager.xml_tree, encoding="unicode")
        self.model = load_model_from_xml(xml)
        self.sim = MjSim(self.model)
        self.manager = manager

        interfaces_mjc = {n: InterfaceMJC(n, self.sim, self.model)
                          for n, c in self.manager.components.items()
                          if 'mjc' in self.manager.data(n)['interfaces']}

        self.init_mjc_interfaces(interfaces_mjc)

        self.interfaces = {n: self.manager.data(n)['interfaces']['mjc'](interfaces_mjc[n])
                           for n, interface_mjc in interfaces_mjc.items()}

        self.viewer = ViewerMJC(self.sim, viewer_mode)

    def init_mjc_interfaces(self, interfaces_mjc):

        items = ['sensor', 'actuator', 'camera']
        for item in items:
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
        self.sim.step()
        x = {self.interfaces[i].step() for i in self.interfaces if hasattr(self.interfaces[i], 'step')}
        self.viewer.step()
