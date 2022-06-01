from yarok.components_manager import component

from yarok.utils.PID import PID
from math import pi


class Robotiq2f85MJCInterfaceMJC:

    def __init__(self, interface):
        self.interface = interface
        P = 0.001
        I = 0
        D = 0
        self.gear = 100
        self.PIDs = [PID(P, I, D) for a in interface.actuators]
        self.move(0.9)

        self.last_query_position = None
        self.at_target_hit_counter = 0

    def at(self):
        return self.q[1] / self.gear

    def is_at(self, a):
        def similar_q(a1, a2):
            return abs(a1 - a2) < 0.02

        at = self.at()

        if self.last_query_position is not None:
            if similar_q(a, self.last_query_position):
                self.at_target_hit_counter += 1

                if self.at_target_hit_counter > 30:
                    self.last_query_position = None
                    self.at_target_hit_counter = 0
                    return True

            else:
                self.last_query_position = None
                self.at_target_hit_counter = 0

        self.last_query_position = at

        return False

    def move(self, a):
        q = [-1 * a, a]
        [self.PIDs[qa].setTarget(q[qa] * self.gear) for qa in range(len(q))]

    def step(self):
        data = self.interface.sensordata()
        self.q = data
        [self.PIDs[a].update(data[a]) for a in range(len(data))]
        [self.interface.set_ctrl(a, self.PIDs[a].output) for a in range(len(self.interface.actuators))]


@component(
    tag='robotiq_2f85',
    interface_mjc=Robotiq2f85MJCInterfaceMJC
)
class robotiq_2f85:

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
