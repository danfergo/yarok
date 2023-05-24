import cv2

import time
import numpy as np
from yarok.core.config_block import ConfigBlock

import mujoco_viewer

def normalize(img):
    img1 = img - np.min(img)
    mx = np.max(img1)
    if mx < 1e-4:
        return img1
    return img1 / mx


class ViewerMJC:
    """
        The MuJoCo viewer wrapper.

        The step method can be called to update the viewer.

    """

    def __init__(self, platform, config: ConfigBlock):
        self.model = platform.model
        self.data = platform.data
        self.config = config
        self.config.defaults({
            'refresh_rate': 1. / 33,
            'width': None,
            'height': None,
            'hide_menus': True
        })


        self.next_probe_ts = time.time() + self.config['refresh_rate']

        self.viewer = mujoco_viewer.MujocoViewer(self.model,
                                                 self.data,
                                                 width=self.config['width'],
                                                 height=self.config['height'],
                                                 hide_menus=self.config['hide_menus'],
                                                 )

    def step(self):
        if time.time() > self.next_probe_ts:
            self.next_probe_ts = time.time() + self.config['refresh_rate']
            self.viewer.render()
