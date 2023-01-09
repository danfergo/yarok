from yarok import component, interface
from yarok.platforms.mjc import InterfaceMJC

from yarok.comm.utils.PID import PID
from math import pi


@interface()
class Robotiq2f85MJCInterfaceMJC:

    def __init__(self, interface: InterfaceMJC):
        self.interface = interface
        # P = 0.001
        # I = 0
        # D = 0
        # self.gear = 100
        # self.PIDs = [PID(P, I, D) for a in interface.actuators]
        # self.move(0.9)
        #
        # self.last_query_position = None
        # self.at_target_hit_counter = 0

    def at(self):
        # return self.q[1] / self.gear
        pass

    def is_at(self, a):
        # def similar_q(a1, a2):
        #     return abs(a1 - a2) < 0.02
        #
        # at = self.at()
        #
        # if self.last_query_position is not None:
        #     if similar_q(a, self.last_query_position):
        #         self.at_target_hit_counter += 1
        #
        #         if self.at_target_hit_counter > 30:
        #             self.last_query_position = None
        #             self.at_target_hit_counter = 0
        #             return True
        #
        #     else:
        #         self.last_query_position = None
        #         self.at_target_hit_counter = 0
        #
        # self.last_query_position = at
        # return False
        pass

    def move(self, a):
        # k = 3.14
        # q = [-1 * a * k * self.gear, a * k * self.gear]
        # [self.PIDs[qa].setTarget(q[qa] * self.gear) for qa in range(2)]
        pass

    def step(self):
        # data = [s / self.gear for s in self.interface.sensordata()]
        # self.q = data
        # print(self.q)
        # [self.PIDs[a].update(data[a]) for a in range(2)]
        [self.interface.set_ctrl(a, 2) for a in range(2)]
        print('')

        # m  = ['finger0_joint1_vel', 'finger1_joint1_vel']
        # [self.interface.set_ctrl(m[a], abs(self.PIDs[a].SetPoint - data[a])) for a in range(2)]


@component(
    tag='robotiq_2f85.py',
    defaults={
        'interface_mjc': Robotiq2f85MJCInterfaceMJC,
        'left_tip': True,
        'right_tip': True
    },
    template_path='robotiq_2f85.xml',
)
class Robotiq2f85:

    def __init__(self):
        pass

    def is_open(self):
        pass

    def is_closed(self):
        pass

    def is_at(self, a):
        pass

    def move(self, a):
        pass

    def open(self):
        self.move(1)

    def close(self):
        self.move(0)
