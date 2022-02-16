from yarok.components.anet_a30.anet_at30 import AnetA30
from yarok.components.cam.cam import Cam
from yarok.mjc.interface import InterfaceMJC
from yarok.components_manager import component

from yarok.components.robotiq_2f85.robotiq_2f85 import robotiq_2f85
from yarok.components.ur5.ur5 import UR5
from yarok.components.gelsight2014.gelsight2014 import gelsight2014
from yarok.components.geltip.geltip import geltip


class EmptyWorldInterfaceMJC:
    def __init__(self, interface: InterfaceMJC):
        self.interface = interface

    def step(self):
        # frame = self.interface.get_frame('extrinsic_cam')
        # print(frame.shape)
        # cv2.imshow('frame', frame)
        # cv2.waitKey(1)
        pass

@component(
    components=[
        UR5,
        robotiq_2f85,
        gelsight2014,
        geltip,
        AnetA30,
        Cam
    ],
    interface_mjc=EmptyWorldInterfaceMJC
)
class EmptyWorld:

    def __init__(self):
        # self.mani = mani
        # print('===> ', mani)
        # pass
        pass

    def init(self):
        # self.mani.move([pi / 2, 0, 0, pi / 2, pi / 2, pi / 2])
        pass