import cv2
from mujoco_py import MjViewerBasic, MjViewer


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

    def __init__(self, sim, mode):
        self.sim = sim
        self.mode = ('' + mode).lower()
        self.frame_counter = 0

        if self.mode == 'view':
            self.mjViewer = MjViewer(self.sim)

    def step(self):
        if self.mode == 'run':
            c_rgb = self.sim.render(width=1000,
                                    height=1000,
                                    depth=False,
                                    camera_name=':extrinsic_cam',
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
