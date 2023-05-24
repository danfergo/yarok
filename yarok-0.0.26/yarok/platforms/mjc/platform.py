from xml.etree.ElementTree import tostring

import mujoco
from mujoco import MjModel

from yarok.core.components_manager import ComponentsManager
from yarok.core.injector import Injector

from ..mjc.interface import InterfaceMJC
from ..mjc.viewer import ViewerMJC
from yarok.core.config_block import ConfigBlock
from yarok.core.platform import Platform
import numpy as np
import cv2
import inspect

INTERFACES_COMPONENTS_NAMES = [
    'sensor',
    'actuator',
    'cam'
]


def adr2name(model, adr):
    return model.names[adr:].decode().split("\x00")[0]


class PlatformMJC(Platform):
    """
        Is the Platform for the MuJoCo simulator

        Manages the environment platform and necessary integrations.

        1. Starts MjSim with the manager.xml_tree
        2. Instantiates the interfaces for each MuJoCo sensor, actuator or camera.
        3. Instantiates the viewer (i.e. ViewerMJC)
        4. Instantiates the components

        Exposes the step() method that steps() through all the interfaces.
    """

    def __init__(self, manager: ComponentsManager, config: ConfigBlock, behaviour):
        super(PlatformMJC, self).__init__(manager, config, behaviour)

        self.model = MjModel.from_xml_string(tostring(manager.xml_tree, encoding="unicode"))
        self.data = mujoco.MjData(self.model)

        self.manager = manager
        self.viewer = ViewerMJC(self, self.config)

        # self.context = MjRenderContextOffscreen(self.sim)

        interfaces_mjc = {id: InterfaceMJC(id, self)
                          for id, c in self.manager.components.items()
                          if 'interface_mjc' in self.manager.config(id)}

        self.init_mjc_interfaces(interfaces_mjc)

        [interf.on_init() for _, interf in interfaces_mjc.items()]

        # ** {'config': config['interfaces'][c['name_path']] or ConfigBlock({})}
        def init_interface(n):
            interface_cls = self.manager.config(n)['interface_mjc']

            # backwards compatible:
            if not hasattr(self.manager.config(n)['interface_mjc'], '__data__'):
                print('[deprecated] interfaces should be annotated with the @interface decorator')
                return interface_cls(interfaces_mjc[n])

            class_members = {t[0]: t[1] for t in inspect.getmembers(interface_cls)}
            init_members = {t[0]: t[1] for t in inspect.getmembers(class_members['__init__'])}
            init_annotations = init_members['__annotations__'] if '__annotations__' in init_members else {}

            interface_defaults = self.manager.config(n)['interface_mjc'].__data__['defaults']
            config = ConfigBlock({})
            config.defaults(interface_defaults)

            providers = [
                {'match_type': ConfigBlock, 'value': config},
                # {'match_all': true, 'factory': lambda name, type: self.platform.manager.get_by_name(self.component_ref, name)['instance']}
                {'match_type': InterfaceMJC, 'value': interfaces_mjc[n]}
            ]

            injector = Injector(self, providers=providers)

            return interface_cls(**injector.get_all(init_annotations))

        self.interfaces = {n: init_interface(n) for n, interface_mjc in interfaces_mjc.items()}

        self.init_components(self.interfaces)

    def init_mjc_interfaces(self, interfaces_mjc):
        """
            Instantiates interfaces for sensors, actuators, and cameras.
        """

        for item in INTERFACES_COMPONENTS_NAMES:
            # print((self.model.names.decode('utf-8')))
            # print((self.model.nnames))

            for idx, adr in enumerate(getattr(self.model, 'name_' + item + 'adr')):
                abs_name = adr2name(self.model, adr)  # getattr(self.model, item + '_id2name')(idx)
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
