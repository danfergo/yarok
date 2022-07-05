import cv2

import time
import numpy as np
from ..config import ConfigBlock

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
        i.e.,
            in the case of VIEW mode
                - is calls mjViewer.render() - the default MuJoCo renderer
            in case of RUN mode
                - it grabs a frame from the default camera and displays
    """

    def __init__(self, platform, config: ConfigBlock):
        self.model = platform.model
        self.data = platform.data
        self.config = config
        self.config.defaults({
            'refresh_rate': 1. / 33,
            'camera_name': 'viewer',
            'resolution': (1920, 1080)
        })


        self.next_probe_ts = time.time() + self.config['refresh_rate']
        self.mode = config['mode']

        self.viewer = mujoco_viewer.MujocoViewer(self.model, self.data)
        self.viewer._hide_menu = True

    def step(self):
        if time.time() > self.next_probe_ts:
            self.next_probe_ts = time.time() + self.config['refresh_rate']
            self.viewer.render()
