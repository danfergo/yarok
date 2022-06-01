import time
import numpy as np
# hacky way of probing
import cv2


def normalize(img):
    if img.dtype == np.uint8:
        return img

    img1 = img - np.min(img)
    mx = np.max(img1)
    if mx < 1e-4:
        return img1
    return img1 / mx


class Inspector:

    def __init__(self, components_manager, platform):
        self.components_manager = components_manager
        self.platform = platform
        self.probe_interval = 1. / 5
        self.next_probe_ts = time.time() + self.probe_interval

    def probe(self):
        """
            Calls probe
        """
        if time.time() > self.next_probe_ts:
            for component_id, comp in self.components_manager.components.items():
                if self.components_manager.data(comp)['probe'] is not None:
                    data = self.components_manager.data(comp)['probe'](comp['instance'])

                    for name, datum in data.items():
                        if type(datum) == np.ndarray:
                            #
                            cv2.imshow(comp['name'] + '/' + name, (normalize(datum) * 255).astype(dtype=np.uint8))
                            cv2.setWindowTitle(comp['name'] + '/' + name, comp['name'] + '/' + name + ', min: ' + str(
                                np.min(datum)) + ' max: ' + str(np.max(datum)))
                # self.platform.sim.step()
                # self.platform.viewer.step()


                            # print(comp['name'])
                            # cv2.waitKey(-1)
            # self.next_probe_ts = time.time() + self.probe_interval + 999999999999999
