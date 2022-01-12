class InterfaceMJC:

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

    def set_ctrl(self, k, v):
        actuator_name = self.actuators[k] if type(k) == int else k
        self.sim.data.ctrl[self.actuator_name2id[actuator_name]] = v


    def sensordata(self):
        return [self.sim.data.sensordata[self.sensor_name2id[sn]] for sn in self.sensors]


    def get_frame(self, camera_name, shape=(480, 640), depth=False):
        return self.sim.render(height=shape[0],
                               width=shape[1],
                               camera_name=self.component_name + ':' + camera_name,
                               depth=depth,
                               mode='offscreen')
