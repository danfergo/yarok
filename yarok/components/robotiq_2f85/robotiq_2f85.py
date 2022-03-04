from yarok.components_manager import component


class Robotiq2f85MJCInterface:

    def __init__(self, interface):
        self.interface = interface

    def move(selfs, a):
        print(a)


@component(
    interface_mj=Robotiq2f85MJCInterface
)
class robotiq_2f85:

    def __init__(self):
        pass

    def is_open(self):
        pass

    def is_closed(self):
        pass

    def move(self, a):
        pass

    def open(self):
        self.move(1)

    def close(self):
        self.move(0)
