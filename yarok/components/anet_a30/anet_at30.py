from yarok.components_manager import component
from yarok.mjc.interface import InterfaceMJC


class AnetA30InterfaceMJC:

    def __init__(self, interface: InterfaceMJC):
        self.interface = interface
        self.gear = 100
        self.target_position = (0, 0, 0)
        self.MAX_X = 320
        self.MAX_Y = 320
        self.MAX_Z = 420

    def move(self, p):
        self.target_position = [
            max(0, min(p[0], self.MAX_X)),
            max(0, min(p[1], self.MAX_Y)),
            max(0, min(p[2], self.MAX_Z))
        ]

    def step(self):
        x, y, z = self.target_position

        self.interface.set_ctrl('ax', (x / 1000.0) * self.gear)
        self.interface.set_ctrl('ay', (y / 1000.0) * self.gear)
        self.interface.set_ctrl('az', (z / 1000.0) * self.gear)


@component(
    interface_mjc=AnetA30InterfaceMJC
)
class AnetA30:

    def __init__(self):
        pass

    def move(self):
        pass
