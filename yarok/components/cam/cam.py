from yarok.components_manager import component
from yarok.mjc.interface import InterfaceMJC


class CameraInterfaceMJC:

    def __init__(self, interface: InterfaceMJC):
        self.interface = interface

    def read(self, depth=False, shape=(480, 640)):
        return self.interface.read_camera('cam', depth, shape)


@component(
    interface_mjc=CameraInterfaceMJC
)
class Cam:

    def __init__(self):
        pass

    def read(self, depth=False, shape=(480, 640)):
        # Implemented by the interface
        pass
