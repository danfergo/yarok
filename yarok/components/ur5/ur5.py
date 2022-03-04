from math import pi

from yarok.utils.PID import PID
from yarok.components_manager import component

import numpy as np
from .ikfastpy import ikfastpy
from scipy.spatial.transform import Rotation as R

# Initialize kinematics for UR5 robot arm
ur5_kin = ikfastpy.PyKinematics()
n_joints = ur5_kin.getDOF()


class UR5InterfaceMJC:
    def __init__(self, interface):
        self.interface = interface
        initial_q = [
            pi / 2,
            0,
            0,
            0,
            0,
            0
        ]
        self.gear = 100
        self.q = initial_q
        P = 1
        I = 0.1
        D = 0.1
        self.PIDs = [PID(P, I, D) for a in interface.actuators]

    def move_q(self, q):
        [self.PIDs[qa].setTarget(q[qa] * self.gear) for qa in range(len(q))]

    def step(self):
        data = self.interface.sensordata()
        self.q = data
        # print(self.q[1], self.PIDs[1].SetPoint, self.PIDs[1].output)
        [self.PIDs[a].update(data[a]) for a in range(len(data))]
        # print(self.PIDs[0].output, self.PIDs[0].output)
        [self.interface.set_ctrl(a, self.PIDs[a].output) for a in range(len(self.interface.actuators))]

    def at(self):
        return self.q
        # pass
        # print(q)


@component(
    interface_mjc=UR5InterfaceMJC,
)
class UR5:

    def __init__(self):
        pass

    def move_q(self, qs):
        pass

    def is_at(self, p):
        pass

    def move_xyz(self, xyz):
        # solve ik, call ikfast from Andy Zeng
        #
        # ee_pose = np.array([[0.04071115, - 0.99870914, 0.03037599, 0.0 ],
        #            [-0.99874455, - 0.04156303, - 0.02796067, 0.2],
        #            [0.0291871, - 0.02919955, - 0.99914742, 0.43451169]])
        # ee_pose = np.array([[1.0, 0.0, 0.0, -0.5],
        #                     [0.0, 1.0, 0.0, -0.5],
        #                     [0.0, 0.0, 1.0, 0.0]])
        #
        # print("\n-----------------------------")
        # print()
        # print()
        # print(ee_pose)
        r = R.from_euler('xyz', [0.1, -180.1, -0.1], degrees=True)
        ee_pose = np.concatenate([r.as_matrix(), np.array([[-0.8, 0.0, 0.0]]).T], axis=1)
        # ee_pose = np.concatenate([ee_pose, np.array([[0, 0, 0, 1.0]])])

        print(ee_pose)
        print(ee_pose.reshape(-1).tolist())

        # Test inverse kinematics: get joint angles from end effector pose
        print("\nTesting inverse kinematics:\n")

        joint_configs = ur5_kin.inverse(ee_pose.reshape(-1).tolist())
        n_solutions = int(len(joint_configs) / n_joints)
        print("%d solutions found:" % (n_solutions))

        joint_configs = np.asarray(joint_configs).reshape(n_solutions, n_joints)

        for joint_config in joint_configs:
            print(joint_config)

        # q = None
        # j = [-pi/2, 0, 0, 0, 0, 0]
        # self.move_q(joint_configs[2])
        self.move_q(joint_configs[3])
