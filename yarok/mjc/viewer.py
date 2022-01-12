import cv2
from mujoco_py import MjViewerBasic, MjViewer


class ViewerMJC:

    def __init__(self, sim, mode):
        self.sim = sim
        self.mode = mode
        self.frame_counter = 0
        print('MODE!!!', mode)
        if self.mode == 'view':
            self.mjViewer = MjViewer(self.sim)
        # if self.mode == 'run':
        # self.sim.step()
        # self.frame_counter += 1
        # if self.frame_counter >= 30:
        # g_rgb = cv2.flip(g_rgb, 1)  # 1, horizontal flip
        # c_rgb = cv2.flip(c_rgb, 1)  # 1, horizontal flip
        #
        # g_rgb = cv2.cvtColor(g_rgb, cv2.COLOR_RGB2BGR)
        # c_rgb = cv2.cvtColor(c_rgb, cv2.COLOR_RGB2BGR)
        #
        # cv2.imshow('geltip', g_rgb)
        # cv2.imshow('global', c_rgb)

        # else:

    def step(self):
        if self.mode == 'run':
                                    # camera_name='global',
            c_rgb = self.sim.render(width=1000,
                                    height=1000,
                                    depth=False,
                                    mode='offscreen')
            c_bgr = cv2.cvtColor(c_rgb, cv2.COLOR_RGB2BGR)
            g_bgr_flip = cv2.flip(c_bgr, 0)
            cv2.imshow('viewer', g_bgr_flip)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                exit()
        else:
            self.mjViewer.render()

    # def viewer_setup(self):
    #     # self.viewer.cam.trackbodyid = 0         # id of the body to track ()
    #     self.viewer.cam.lookat[0] += 0  # x,y,z offset from the object (works if trackbodyid=-1)
    #     self.viewer.cam.lookat[1] += 0
    #     self.viewer.cam.lookat[2] += 0
    #     self.viewer.cam.distance = 0.8  # how much you "zoom in", model.stat.extent is the max limits of the arena
    #     self.viewer.cam.elevation = 0  # camera rotation around the axis in the plane going through the frame origin (if 0 you just see a line)
    #     self.viewer.cam.azimuth = 0  # camera rotation around the camera's vertical axis
