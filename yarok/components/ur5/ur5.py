from math import pi

from yarok.utils.PID import PID
from yarok.components_manager import component


class UR5InterfaceMJC:
    def __init__(self, interface):
        self.interface = interface
        initial_q = [
            pi / 2,
            0,
            0,
            0,
            0,
            0
        ]
        self.gear = 100
        P = 100
        I = 0.001
        D = 0.001
        self.PIDs = [PID(P, I, D) for a in interface.actuators]

    def move_q(self, q):
        # print(q)
        [self.PIDs[qa].setTarget(q[qa]) for qa in range(len(q))]
        # pass

    def step(self):
        data = self.interface.sensordata()
        [self.PIDs[a].update(data[a]) for a in range(len(data))]
        [self.interface.set_ctrl(a, self.PIDs[a].output) for a in range(len(self.interface.actuators))]


@component(
    interface_mjc=UR5InterfaceMJC,
)
class UR5:

    def __init__(self):
        pass

    def move_q(self, qs):
        pass

    def move(self, q):
        self.move_q(q)

    def move_xyz(self, xyz):
        # solve ik, call ikfast from Andy Zeng
        q = None
        self.move(q)
        pass