from xml.etree.ElementTree import tostring

import mujoco
from mujoco import MjModel

from ..components_manager import ComponentsManager
from ..mjc.interface import InterfaceMJC
from ..mjc.viewer import ViewerMJC
from ..config import ConfigBlock

import numpy as np
import cv2

INTERFACES_COMPONENTS_NAMES = [
    'sensor',
    'actuator',
    'cam'
]


def adr2name(model, adr):
    return model.names[adr:].decode().split("\x00")[0]

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

    def __init__(self, manager: ComponentsManager, config: ConfigBlock):
        self.config = config['platform'] if config.is_config_block('platform') else ConfigBlock({
            'class': config['platform']
        })
        self.config.defaults({
            'viewer': {}
        })

        self.model = MjModel.from_xml_string(tostring(manager.xml_tree, encoding="unicode"))
        self.data = mujoco.MjData(self.model)

        self.manager = manager
        # self.sim = MjSim(self.model)
        self.viewer = ViewerMJC(self, self.config['viewer'])

        # self.context = MjRenderContextOffscreen(self.sim)

        interfaces_mjc = {id: InterfaceMJC(id, self)
                          for id, c in self.manager.components.items()
                          if 'mjc' in self.manager.data(id)['interfaces']}

        self.init_mjc_interfaces(interfaces_mjc)

        [interf.on_init() for _, interf in interfaces_mjc.items()]

        # ** {'config': config['interfaces'][c['name_path']] or ConfigBlock({})}

        self.interfaces = {n: self.manager.data(n)['interfaces']['mjc'](
            interfaces_mjc[n]
        ) for n, interface_mjc in interfaces_mjc.items()}


        manager.init_components(self.interfaces, config['components'])


    def init_mjc_interfaces(self, interfaces_mjc):
        """
            Instantiates interfaces for sensors, actuators, and cameras.
        """

        for item in INTERFACES_COMPONENTS_NAMES:
           # print((self.model.names.decode('utf-8')))
           # print((self.model.nnames))

            for idx, adr in enumerate(getattr(self.model, 'name_' + item + 'adr')):
                abs_name = adr2name(self.model, adr) #getattr(self.model, item + '_id2name')(idx)
                col_idx = abs_name.index(':')
                component_name = abs_name[:col_idx]
                item_name = abs_name[col_idx + 1:]

                if component_name in interfaces_mjc:
                    interface = interfaces_mjc[component_name]
                    getattr(interface, item + '_name2idx')[item_name] = idx
                    getattr(interface, item + '_name2adr')[item_name] = adr
                    getattr(interface, item + 's').append(item_name)
                    interface.component_name = component_name

    def step(self):
        """
            Steps through all the interfaces
        """
        mujoco.mj_step(self.model, self.data)
        _ = {self.interfaces[i].step() for i in self.interfaces if hasattr(self.interfaces[i], 'step')}
        self.viewer.step()

