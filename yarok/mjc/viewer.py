import cv2
from mujoco_py import MjViewerBasic, MjViewer, MjRenderContextOffscreen, MjRenderContextWindow, MjRenderContext

import time
import numpy as np
from ..config import ConfigBlock


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
        self.sim = platform.sim
        self.model = platform.model
        self.config = config
        self.config.defaults({
            'mode': 'opencv',  # or native,
            'refresh_rate': 1. / 12,
            'camera_name': 'viewer',
            'resolution': (1920, 1080)
        })


        self.next_probe_ts = time.time() + self.config['refresh_rate']
        self.mode = config['mode']

        if self.config['mode'] == 'opencv':
            self.viewer = MjRenderContext(sim=self.sim, device_id=0, offscreen=True, opengl_backend='glfw')

            rel_cam_name = self.config['camera_name']
            cam_names = list(self.model.camera_names)
            cam_name = next(filter(lambda n: n.split(':')[1] == rel_cam_name, cam_names), None)

            if cam_name is None:
                raise Exception(
                    ('No camera with name "{cam_name}" has been found. Define it in the world template ' + \
                    'or adjust the viewer configuration with the camera name be used.').format(cam_name=rel_cam_name))

            self.camera_id = self.model.camera_name2id(cam_name)
            self.wh = tuple(self.config['resolution'])
        else:
            self.mjViewer = MjViewer(self.sim)

    def step(self):
        if time.time() > self.next_probe_ts:

            self.next_probe_ts = time.time() + self.config['refresh_rate']
            if self.mode == 'opencv':
                self.viewer \
                    .render(
                    width=self.wh[0],
                    height=self.wh[1],
                    camera_id=self.camera_id
                )
                rgb, d = self.viewer.read_pixels(
                    width=self.wh[0],
                    height=self.wh[1],
                    depth=True
                )
                c_bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)[::-1, :, :]
                cv2.imshow("viewer", c_bgr)
                pass
            else:
                self.mjViewer.render()

                # c_rgb = self.context_offscreen.read_pixels_depth(
                #     self.depth_arr
                # )

                #
                # return frame

                #
                # c_rgb = self.sim.render(width=640,
                #                         height=480,
                #                         depth=False,
                #                         camera_name=':extrinsic_cam',
                #                         mode='offscreen')

                #
                # c_bgr = cv2.cvtColor(frame[0], cv2.COLOR_RGB2BGR)
                # g_bgr_flip = cv2.flip(c_bgr, 0)
                # cv2.imshow('viewer', g_bgr_flip)
                # cv2.imshow('viewer_depth', normalize(frame[1]))
                # print('viewer')
                # cv2.waitKey(-1)
                # print(self.i, 'end')
                # self.i += 1
                # print('- > draw..')
                # return True

            # print('xxx')
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     exit()
            # else:
            #     print('skip..')

            # print('..')

            # 640, 480
            # camera_id = self.model.camera_name2id('#1__::extrinsic_cam')
            #

            # self.context_offscreen \
            #     .render(height=480,
            #             width=640,
            #             camera_id=-1
            #             )
            # #
            # frame = self.context_offscreen.read_pixels(
            #     height=shape[0],
            #     width=shape[1],
            #     depth=True
            # )

            # self.context_offscreen.read_pixels_depth(
            #     self.depth_arr
            # )

            # print('before render 1 ')
            # self.context_offscreen \
            #     .render(
            #     width=640,
            #     height=480,
            #     camera_id=1
            # )
            #
            # frame, depth = self.context_offscreen.read_pixels(
            #     width=640,
            #     height=480,
            #     depth=True
            # )

            # cv2.imshow('pixels', frame)
            # cv2.waitKey(-1)
            # print('waited1')
            #
            # print('before render 2 (viewer) ')

            # self.context_offscreen \
            #     .render(
            #     width=640,
            #     height=480,
            #     camera_id=0
            # )

            # self.context_offscreen \
            #     .render(
            #     width=640,
            #     height=480,
            #     camera_id=0
            # )
            #
            # frame, depth = self.context_offscreen.read_pixels(
            #     width=640,
            #     height=480,
            #     depth=True
            # )

            # cv2.imshow('viewer', frame)
            # cv2.waitKey(-1)
            # print('waited2')

            # camera_id = self.model.camera_name2id('#1:extrinsic_cam')
            #
            # #

            # self.mjViewer \
            #     .render(height=shape[0],
            #             width=shape[1],
            #             camera_id=camera_id
            #             )
            #
            # frame = self.platform.context_offscreen.read_pixels(
            #     height=shape[0],
            #     width=shape[1],
            #     depth=depth
            # )
    # def viewer_setup(self):
    #     # self.viewer.cam.trackbodyid = 0         # id of the body to track ()
    #     self.viewer.cam.lookat[0] += 0  # x,y,z offset from the object (works if trackbodyid=-1)
    #     self.viewer.cam.lookat[1] += 0
    #     self.viewer.cam.lookat[2] += 0
    #     self.viewer.cam.distance = 0.8  # how much you "zoom in", model.stat.extent is the max limits of the arena
    #     self.viewer.cam.elevation = 0  # camera rotation around the axis in the plane going through the frame origin (if 0 you just see a line)
    #     self.viewer.cam.azimuth = 0  # camera rotation around the camera's vertical axis
