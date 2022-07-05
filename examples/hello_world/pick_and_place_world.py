from yarok.components.anet_a30.anet_at30 import AnetA30
from yarok.components.cam.cam import Cam
from yarok.mjc.interface import InterfaceMJC
from yarok.components_manager import component

from yarok.components.robotiq_2f85.robotiq_2f85 import robotiq_2f85
from yarok.components.ur5.ur5 import UR5
from yarok.components.gelsight.gelsight2014 import gelsight2014
from yarok.components.geltip.geltip import GelTip


class PickAndPlaceWorldInterfaceMJC:
    def __init__(self, interface: InterfaceMJC):
        self.interface = interface

    def step(self):
        # print('---> ', self.interface.sensors)
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
        GelTip,
        AnetA30,
        Cam
    ],
    interface_mjc=PickAndPlaceWorldInterfaceMJC,
)
class PickAndPlaceWorld:

    def __init__(self, arm: UR5):
        self.arm = arm
        # print('===> ', mani)
        # pass
        pass

    def init(self):
        # self.mani.move([pi / 2, 0, 0, pi / 2, pi / 2, pi / 2])
        pass

    def step(self):
        pass
