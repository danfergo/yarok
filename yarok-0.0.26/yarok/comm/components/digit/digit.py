from yarok import ConfigBlock, Platform, component, interface
from yarok.platforms.mjc import InterfaceMJC

import numpy as np
import cv2
import os

import math
from time import time

from .utils.phong_render import PhongRender

gel_width, gel_height = 240, 320

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


@interface(
    defaults={
        'light_sources': [
            {'position': [-0.866, 0.5, 0.25], 'color': (255, 82, 108), 'kd': 0.1, 'ks': 0.4},
            # red, bottom (108, 82, 255) kd 0.6
            {'position': [0.866, 0.5, 0.25], 'color': (153, 255, 120), 'kd': 0.1, 'ks': 0.4},
            # green, left (120, 255, 153)
            {'position': [0, -1, 0.25], 'color': (115, 130, 255), 'kd': 0.3, 'ks': 0.4},
            # blue, left (255, 130, 115)
        ],
        'background_img': cv2.cvtColor(
            cv2.imread(os.path.join(__location__, './assets/gel/digit_bg.png')),
            cv2.COLOR_BGR2RGB),
        'ka': 1.0,
        'texture_sigma': 0.00001,
        'px2m_ratio': 5.4347826087e-05,
        'elastomer_thickness': 1.0,
        'min_depth': 0.0
    }
)
class DigitInterfaceMJC:

    def __init__(self, interface: InterfaceMJC, config: ConfigBlock):
        self.interface = interface
        self.simulation = PhongRender(
            light_sources=config['light_sources'],
            background_img=config['background_img'],
            ka=config['ka'],
            texture_sigma=config['texture_sigma'],
            px2m_ratio=config['px2m_ratio'],
            elastomer_thickness=config['elastomer_thickness'],
            min_depth=config['min_depth']
        )
        self.last_update = 0
        self.depth = np.zeros((320, 240), np.float32)

    def read(self, shape=(320, 240)):
        t = time()
        if self.last_update > t - 1.0:
            return self.tactile
        self.last_update = t
        self.depth = self.interface.read_camera('digit0:camera', shape, depth='raw', rgb=False)
        self.tactile = self.simulation.generate(self.depth).astype(np.uint8)

        return self.tactile

    def read_depth(self):
        return self.depth


class DigitInterfaceHW:

    def __init__(self, config: ConfigBlock):
        self.cap = cv2.VideoCapture(config['cam_id'])
        if not self.cap.isOpened():
            raise Exception('Digit cam ' + str(config['cam_id']) + ' not found')

        self.fake_depth = np.zeros((240, 320), np.float32)

    def read(self):
        [self.cap.read() for _ in range(10)]  # skip frames in the buffer.
        ret, frame = self.cap.read()
        return frame

    def read_depth(self):
        return self.fake_depth


@component(
    tag="digit",
    defaults={
        'interface_mjc': DigitInterfaceMJC,
        'interface_hw': DigitInterfaceHW,
        'probe': lambda c: {'camera': c.read()},
    },
    template_path='digit.xml'
)
class Digit:

    def __init__(self):
        """
            DIGIT simulation as proposed in
            https://github.com/Rancho-zhao/Digit_PhongSim
        """
        pass

    def read(self):
        pass

    def read_depth(self):
        pass


if __name__ == '__main__':
    Platform.create({
        'world': Digit
    }).run()
