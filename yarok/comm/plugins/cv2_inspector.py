import time
import numpy as np
import cv2

from yarok import Platform


def normalize(img):
    if img.dtype == np.uint8:
        return img

    img1 = img - np.min(img)
    mx = np.max(img1)
    if -1e-6 < mx < 1e-6:
        return img1.astype(dtype=np.uint8)
    return ((img1 / mx) * 255).astype(dtype=np.uint8)

def torgb(img):
    if len(img.shape) == 3:
        return img

    return np.stack([img, img, img], axis=2)

class Cv2Inspector:

    def __init__(self, platform: Platform):
        self.components_manager = platform.manager
        self.platform = platform
        self.probe_interval = 0.5
        self.next_probe_ts = time.time() + self.probe_interval

    def inspect_component(self, comp):
        data = self.components_manager.config(comp)['probe'](comp['instance'])

        for name, datum in data.items():
            if type(datum) == np.ndarray:
                frame = datum.copy()
                frame = normalize(frame)
                frame = torgb(frame)
                minx_max_txt = "{:.3f}".format(np.min(datum)) + ' - ' + "{:.3f}".format(np.max(datum))
                frame = cv2.putText(frame, minx_max_txt, (20, 20),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5,
                                    (0, 255, 0),
                                    1,
                                    cv2.LINE_AA)
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.imshow(comp['name'] + '/' + name, frame_bgr)
                cv2.setWindowTitle(comp['name'] + '/' + name, comp['name'] + '/' + name)

    def step(self):
        """
            Calls probe
        """
        if time.time() > self.next_probe_ts:
            [
                self.inspect_component(comp)
                for component_id, comp in self.components_manager.components.items()
                if 'probe' in self.components_manager.config(comp)
            ]
            self.next_probe_ts = time.time() + self.probe_interval

            cv2.waitKey(1)
