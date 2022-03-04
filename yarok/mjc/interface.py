class InterfaceMJC:
    """
        This Interface serves as a simplified MuJoCo api,
        it handles lower level naming/referencing and offers an object/component oriented interface.

        It is instantiated and passed to the constructor of each corresponding component MuJoCo's interface.
    """

    def __init__(self, name, sim, model):
        self.component_name = name
        self.sim = sim
        self.model = model
        self.sensor_name2id = {}
        self.actuator_name2id = {}
        self.camera_name2id = {}
        self.actuators = []
        self.sensors = []
        self.cameras = []
        self.component_name = ''

    # https://github.com/htung0101/table_dome/blob/master/table_dome_calib/utils.py#L160
    def depthimg2Meters(self, depth):
        extent = self.model.stat.extent
        near = self.model.vis.map.znear * extent
        far = self.model.vis.map.zfar * extent
        image = near / (1 - depth * (1 - near / far))
        return image

    def set_ctrl(self, k, v):
        actuator_name = self.actuators[k] if type(k) == int else k
        self.sim.data.ctrl[self.actuator_name2id[actuator_name]] = v

    def sensordata(self):
        return [self.sim.data.sensordata[self.sensor_name2id[sn]] for sn in self.sensors]

    def read_camera(self, camera_name, shape=(480, 640), depth=False):
        frame = self.sim.render(height=shape[0],
                                width=shape[1],
                                camera_name=self.component_name + ':' + camera_name if len(
                                    self.component_name) > 0 else camera_name,
                                depth=depth,
                                mode='offscreen')

        if not depth:
            return frame
        else:
            rgb, depth = frame
            return rgb, self.depthimg2Meters(depth)
