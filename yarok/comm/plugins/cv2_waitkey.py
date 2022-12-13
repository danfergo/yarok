import cv2

from yarok.core.config_block import ConfigBlock


class Cv2WaitKey:

    def __init__(self, config: ConfigBlock):
        self.config = config

    def step(self):
        cv2.waitKey(self.config['ms'] or 1)
