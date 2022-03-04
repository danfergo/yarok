import time
import numpy as np
# hacky way of probing
import cv2

def normalize(img):
    img1 = img - np.min(img)
    mx = np.max(img1)
    if mx < 1e-4:
        return img1
    return img1 / mx

class Inspector:

    def __init__(self, components_manager):
        self.components_manager = components_manager
        self.probe_interval = 1. / 12
        self.next_probe_ts = time.time() + self.probe_interval



    def probe(self):
        """
            Calls probe
        """
        if time.time() > self.probe_interval:
            for component_id, comp in self.components_manager.components.items():
                if self.components_manager.data(comp)['probe'] is not None:
                    data = self.components_manager.data(comp)['probe'](comp['instance'])
                    for name, datum in data.items():
                        if type(datum) == np.ndarray:
                            #
                            cv2.imshow(name,  (normalize(datum) * 255).astype(dtype=np.uint8))
                            cv2.setWindowTitle(name, name + ', min: ' + str(np.min(datum)) + ' max: ' + str(np.max(datum)))

                cv2.waitKey(1)
            self.next_probe_ts = time.time() + self.probe_interval
