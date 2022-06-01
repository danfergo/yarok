from mujoco_py import MjRenderContextOffscreen, MjRenderContextWindow, MjRenderContext

import numpy as np


class InterfaceMJC:
    """
        This Interface serves as a simplified MuJoCo api,
        it handles lower level naming/referencing and offers an object/component oriented interface.

        It is instantiated and passed to the constructor of each corresponding component MuJoCo's interface.
    """

    def __init__(self, name, platform):
        global offscreen_id
        self.component_name = name
        self.platform = platform
        self.sensor_name2id = {}
        self.actuator_name2id = {}
        self.camera_name2id = {}
        self.actuators = []
        self.sensors = []
        self.cameras = []
        self.component_name = ''
        self.contexts = {}

    def on_init(self):
        self.contexts = {
            cam_name: MjRenderContext(sim=self.platform.sim, device_id=0, offscreen=True, opengl_backend='glfw')
            for cam_name in self.camera_name2id
        }

    # https://github.com/htung0101/table_dome/blob/master/table_dome_calib/utils.py#L160
    def depthimg2Meters(self, depth):
        extent = self.platform.model.stat.extent
        near = self.platform.model.vis.map.znear * extent
        far = self.platform.model.vis.map.zfar * extent
        image = near / (1 - depth * (1 - near / far))
        return image

    def set_ctrl(self, k, v):
        actuator_name = self.actuators[k] if type(k) == int else k
        self.platform.sim.data.ctrl[self.actuator_name2id[actuator_name]] = v

    def sensordata(self):
        return [self.platform.sim.data.sensordata[self.sensor_name2id[sn]] for sn in self.sensors]

    def read_camera(self, camera_name, shape=(480, 640), depth=False, rgb=True):
        """
            mj_(offscreen)context.render() api:
            https://github.com/openai/mujoco-py/blob/master/mujoco_py/mjrendercontext.pyx#L131

            mj_(offscreen)context.read_pixels() api:
            https://github.com/openai/mujoco-py/blob/master/mujoco_py/mjrendercontext.pyx#L176

            and for ref, mjSim render()
            https://github.com/openai/mujoco-py/blob/master/mujoco_py/mjsim.pyx#L131
        """

        context = self.contexts[camera_name]
        camera_id = self.camera_name2id[camera_name]

        self.depth_arr = np.zeros((480, 640), dtype=np.float32)

        context.render(height=shape[0],
                       width=shape[1],
                       camera_id=camera_id
                       )
        if rgb:
            rgb, d = context.read_pixels(
                height=shape[0],
                width=shape[1],
                depth=True
            )

            if depth:
                return rgb[::-1, :, :], \
                       self.depthimg2Meters(d)[::-1, :]
            else:
                return rgb

        else:
            self.context_offscreen.read_pixels_depth(
                self.depth_arr
            )
            return self.depth_arr
