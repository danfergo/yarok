# from mujoco import MjRenderContextOffscreen, MjRenderContextWindow, MjRenderContext

import numpy as np
import mujoco


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
        self.sensor_name2adr = {}
        self.actuator_name2adr = {}
        self.cam_name2adr = {}
        self.sensor_name2idx = {}
        self.actuator_name2idx = {}
        self.cam_name2idx = {}
        self.actuators = []
        self.sensors = []
        self.cams = []
        self.component_name = ''
        self.contexts = {}
        self.scn = mujoco.MjvScene(self.platform.model, maxgeom=10000)
        self.vopt = mujoco.MjvOption()
        self.pert = mujoco.MjvPerturb()

    def on_init(self):
        self.contexts = {
            cam_name: mujoco.MjrContext(self.platform.model, mujoco.mjtFontScale.mjFONTSCALE_150.value)
            for cam_name in self.cam_name2adr
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
        self.platform.data.ctrl[self.actuator_name2idx[actuator_name]] = v

    def sensordata(self):
        return [self.platform.data.sensordata[self.sensor_name2idx[sn]] for sn in self.sensors]

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
        camera_id = self.cam_name2idx[camera_name]

        self.depth_arr = np.zeros(shape, dtype=np.float32)
        self.rgb = np.zeros(shape + (3,), dtype=np.uint8)

        viewport = mujoco.MjrRect(0, 0, shape[1], shape[0])

        cam = mujoco.MjvCamera()
        cam.type = 2
        cam.fixedcamid = camera_id

        mujoco.mjv_updateScene(
            self.platform.model,
            self.platform.data,
            self.vopt,
            self.pert,
            cam,
            mujoco.mjtCatBit.mjCAT_ALL.value,
            self.scn)

        mujoco.mjv_defaultCamera(cam)
        mujoco.mjr_render(viewport, self.scn, context)
        mujoco.mjr_readPixels(self.rgb, self.depth_arr, viewport, context)

        self.rgb = np.fliplr(self.rgb)
        self.depth_arr = np.fliplr(self.depth_arr)

        if not depth:
            return self.rgb
        d = self.depth_arr if depth == 'raw' else self.depthimg2Meters(self.depth_arr)

        if not rgb:
            return d

        return self.rgb, d
