from yarok.components_manager import component
from yarok.mjc.interface import InterfaceMJC


class CameraInterfaceMJC:

    def __init__(self, interface: InterfaceMJC):
        self.interface = interface

    def get_frame(self):
        return self.interface.get_frame('cam')


@component(
    interface_mjc=CameraInterfaceMJC
)
class Cam:

    def __init__(self):
        pass
