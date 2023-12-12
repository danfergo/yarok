import cv2

import time
import numpy as np
from yarok.core.config_block import ConfigBlock

import mujoco_viewer
import glfw


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
        self.config = ConfigBlock(config)
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
        self.interfaces = []
        self.pass_through_mjc_viewer = False
        glfw.set_key_callback(self.viewer.window, self.key_event)

    def key_event(self, window, key, scancode, action, mods):
        assert action < 3, f'Unkown glfw action {action}'
        event = 'down' if action == 1 else ('up' if action == 0 else 'press')
        keypress = action == 1 or action == 2
        keydown = action == 1
        keyup = action == 0

        if keydown and key == 290:  # f1
            self.pass_through_mjc_viewer = not self.pass_through_mjc_viewer

        if self.pass_through_mjc_viewer:
            # pass-through to mujoco-viewer callback
            self.viewer._key_callback(window, key, scancode, action, mods)
        else:
            # call keys from interfaces
            if keypress:
                _ = {self.interfaces[i].on_keypress(key) for i in self.interfaces if
                     hasattr(self.interfaces[i], 'on_keypress')}

            if keyup:
                _ = {self.interfaces[i].on_keyup(key) for i in self.interfaces if
                     hasattr(self.interfaces[i], 'on_keyup')}

            if keydown:
                _ = {self.interfaces[i].on_keydown(key) for i in self.interfaces if
                     hasattr(self.interfaces[i], 'on_keydown')}

    def step(self):
        if time.time() > self.next_probe_ts:
            self.next_probe_ts = time.time() + self.config['refresh_rate']
            self.viewer.render()
