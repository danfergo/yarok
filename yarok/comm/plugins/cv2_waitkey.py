import cv2

from yarok.core.config_block import ConfigBlock


class Cv2WaitKey:

    def __init__(self, config: ConfigBlock):
        self.config = config
        self.wait_ms = self.config['wait_ms'] if 'wait_ms' in self.config else 1
        self.skip_s = (self.config['skip_ms'] if 'skip_ms' in self.config else 100) / 1000
        self.next_probe_ts = time.time()

    def step(self):
        if time.time() > self.next_probe_ts:
            cv2.waitKey(self.config['ms'] or 1)
            key = cv2.waitKey(self.wait_ms)
            self.next_probe_ts = time.time() * self.skip_s
