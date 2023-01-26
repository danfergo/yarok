import os
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

import subprocess

if not os.path.exists(os.path.join(__location__, 'ikfastpy')):
    print('To enable UR5e pose control, Andy Zeng ikfastpy is going to be cloned and installed.')
    print('https://github.com/andyzeng/ikfastpy')
    print('Insert [Y] to continue... else aborts')
    if input('') == 'Y':
        process = subprocess.Popen([os.path.join(__location__, 'install_ikfast.sh'), __location__])
        process.wait()
        print('Done. Finished installing ikfastpy.')
    else:
        exit(-1)

from yarok import Platform, PlatformMJC, PlatformHW, component, interface, ConfigBlock, Injector

from yarok.platforms.mjc import InterfaceMJC

from math import pi, sin, cos
import time
import numpy as np
from scipy.spatial.transform import Rotation as R
from .ikfastpy import ikfastpy


def sae(q1, q2):
    return sum([abs(q1[i] - q2[i]) for i in range(6)])


@interface(
    # max-speed https://store.clearpathrobotics.com/products/ur5e
    defaults={
        'speed': pi / 24
    }
)
class UR5eInterfaceMJC:
    def __init__(self, interface: InterfaceMJC, config: ConfigBlock):
        self.interface = interface
        self.speed = config['speed']
        initial_q = [
            0,
            0,
            0,
            0,
            0,
            0
        ]

        self.ws = [
            [- pi, pi],  # shoulder pan
            [- pi, 0],  # shoulder lift,
            [- 2 * pi, 2 * pi],  # elbow
            [-2 * pi, 2 * pi],  # wrist 1
            [- 2 * pi, 2 * pi],  # wrist 2
            [- 2 * pi, 2 * pi]  # wrist 3
        ]
        self.stopped_steps = 0

        self.q = initial_q
        self.start_q = initial_q
        self.target_q = initial_q
        self.start_t = time.time()
        self.delta_t = 0

        self.ur5_kin = ikfastpy.PyKinematics()
        self.n_joints = self.ur5_kin.getDOF()

        # transformation_matrix = np.array([[0.04071115, -0.99870914, 0.03037599, 0.3020009],
        #                                   [-0.99874455, -0.04156303, -0.02796067, 0.12648243],
        #                                   [0.0291871, -0.02919955, -0.99914742, 0.53451169]])
        # print(self.get_pose_vectors(transformation_matrix))

        # ee_pose = HTrans(np.array([self.q]).T, [0])  # self.ur5_kin.forward(self.q)
        # ee_pose = np.asarray(ee_pose)
        # ee_pose = np.asarray(ee_pose).reshape(3, 4)  # 3x4 rigid transformation matrix
        # print('INITIAL transformation matrix ')
        # print(ee_pose)
        # rotation_matrix = ee_pose[0:3, 0:3]
        # translation_matrix = ee_pose[0:3, 3].T
        # xyz = R.from_matrix(rotation_matrix).as_euler('xyz')
        # print('Initial translation', translation_matrix, 'Initial rotation (xyz): ', xyz)

    def get_transformation_matrix(self, q):
        ee_pose = self.ur5_kin.forward(q)
        ee_pose = np.asarray(ee_pose).reshape(3, 4)
        return ee_pose

    def get_pose_vectors(self, transformation_matrix):
        # print(ee_pose)
        rotation_matrix = transformation_matrix[0:3, 0:3]
        xyz = transformation_matrix[0:3, 3].T
        xyz_angles = R.from_matrix(rotation_matrix).as_euler('xyz')
        # print('----')
        # print(current_xyz)
        # print(current_xyz_angles)
        # print('----')
        # print(R.from_euler('xyz', current_xyz_angles).as_matrix())
        return xyz, xyz_angles

    def compute_transformation_matrix(self, xyz, xyz_angles):
        rotation_matrix = R.from_euler('xyz', xyz_angles).as_matrix()
        return np.concatenate([rotation_matrix, np.array([xyz]).T], axis=1)

    def compute_ik(self, transformation_matrix):

        joint_configs = self.ur5_kin.inverse(transformation_matrix.reshape(-1).tolist())
        n_solutions = int(len(joint_configs) / self.n_joints)
        joint_configs = np.asarray(joint_configs).reshape(n_solutions, self.n_joints)

        if n_solutions == 0:
            print('[Error] no solutions found for this pose')
            return None

        valid_config = lambda config: not any([not (self.ws[i][0] < config[i] < self.ws[i][1]) for i in range(6)])
        valid_joint_configs = [config for config in joint_configs if valid_config(config)]

        if len(valid_joint_configs) == 0:
            print('Configs outside the workspace:')
            print(joint_configs)
            print('[Error] no solutions within the workspace')
            return None

        closest_config_index = np.argmin([sae(self.q, q) for q in valid_joint_configs])
        q = valid_joint_configs[closest_config_index]
        return q

    def move_xyz_delta(self, xyz=None, xyz_angles=None):
        c_transformation_matrix = self.get_transformation_matrix(self.q)
        current_xyz, current_xyz_angles = self.get_pose_vectors(c_transformation_matrix)
        q_xyz = current_xyz if xyz is None else np.add(current_xyz, xyz)
        q_xyz_angles = current_xyz_angles if xyz_angles is None else np.add(current_xyz_angles, xyz_angles)
        transformation_matrix = self.compute_transformation_matrix(q_xyz, q_xyz_angles)
        q = self.compute_ik(transformation_matrix)

        if q is not None:
            return self.move_q(q)

    def move_xyz(self, xyz=None, xyz_angles=None):
        # xyz = [0.3, 0.3, 0.2]
        # xyz_angles = [pi/2, pi/2 , 0]
        # xyz = None
        # xyz_angles = None
        c_transformation_matrix = self.get_transformation_matrix(self.q)
        current_xyz, current_xyz_angles = self.get_pose_vectors(c_transformation_matrix)
        q_xyz = xyz or current_xyz
        q_xyz_angles = xyz_angles or current_xyz_angles
        # print('CURRENT ANGLES', current_xyz_angles, q_xyz_angles)
        transformation_matrix = self.compute_transformation_matrix(q_xyz, q_xyz_angles)
        q = self.compute_ik(transformation_matrix)

        if q is not None:
            return self.move_q(q)

        # ee_pose = HTrans(np.array([self.q]).T, [0])  # self.ur5_kin.forward(self.q)
        # ee_pose = np.asarray(ee_pose)
        # current_rotation_matrix = ee_pose[0:3, 0:3]
        # current_translation_vector = ee_pose[0:3, 3].T
        # current_xyz_angles = R.from_matrix(current_rotation_matrix).as_euler('xyz')
        # print('Current translation', current_translation_vector, 'rotation (xyz): ', current_xyz_angles)
        #
        # # rotation_matrix = euler_angles([0, 1.6, 0])
        # # print(rotation_matrix)
        # # rotation_matrix = R.from_euler('xyz', [1.6/2, 0, 1.6]).as_matrix()
        # translation_vector = np.array([current_translation_vector if xyz is None else xyz]).T
        # rotation_matrix = current_rotation_matrix if xyz_angles is None else R.from_euler('xyz', xyz_angles).as_matrix()
        # transformation_matrix = np.concatenate([rotation_matrix, translation_vector], axis=1)
        # # print(translation_vector.T.shape, rotation_matrix.shape)
        # # print('transformation matrix', transformation_matrix)
        # # rot_matrix = np.concatenate([, ], axis=1)
        # # rot_matrix = rot_matrix[..., np.newaxis]
        #
        # # transformation_matrix = np.array([[0.04071115, -0.99870914, 0.03037599, 0.3020009],
        # #                     [-0.99874455, -0.04156303, -0.02796067, 0.12648243],
        # #                     [0.0291871, -0.02919955, -0.99914742, 0.53451169]])
        # transformation_matrix_h = np.concatenate([transformation_matrix, np.array([[0, 0, 0, 1]])], axis=0)
        # joint_configs = invKine(transformation_matrix_h)
        # # joint_configs = self.ur5_kin.inverse(transformation_matrix.reshape(-1).tolist())
        # n_solutions = len(joint_configs)
        # # print('>>', joint_configs)
        # # print('--------------')
        # # print('>>', np.array(joint_configs[0])[0])
        # # n_solutions = int(len(joint_configs) / self.n_joints)
        # # joint_configs = np.asarray(joint_configs).reshape(n_solutions, self.n_joints)
        #
        # joint_configs = np.asarray(joint_configs)
        #
        # # print(n_solutions)
        # # # for joint_config in joint_configs:
        # # #     print(joint_config)
        # # print(joint_configs)
        # # print('-----')
        # # print(valid_joint_configs)
        # # print('-----')
        #
        # #
        # # print(n_solutions, closest_config_index, q)
        #
        # # q = [-3.1, -1.6, 1.6, -1.6, -1.6, 0.]
        # self.move_q(q)

    def move_q(self, q):
        self.start_q = self.target_q
        self.target_q = q
        self.start_t = time.time()
        self.delta_t = max([abs(self.target_q[i] - self.start_q[i]) / self.speed for i in range(6)])
        return lambda: self.is_at(q)

    def step(self):
        self.last_q = self.q
        self.q = self.interface.sensordata()
        now = time.time()
        # print(self.q[1])
        if self.start_q is not None:
            elapsed = (now - self.start_t)
            progress = min(1, elapsed / self.delta_t) if self.delta_t > 0 else 1
            target = [(1 - progress) * self.start_q[i] + progress * self.target_q[i] for i in range(6)]
            # print(target)
        else:
            target = self.target_q

        [self.interface.set_ctrl(a, target[a]) for a in range(len(self.interface.actuators))]

        if sae(self.last_q, self.q) < 1e-6:
            self.stopped_steps += 1
        else:
            self.stopped_steps = 0

    def at(self):
        return self.q

    def at_xyz(self):
        transformation_matrix = self.get_transformation_matrix(self.q)
        return self.get_pose_vectors(transformation_matrix)

        # return [q / self.gear for q in self.q]

    def is_at(self, q):
        # s = sum([abs(self.q[i] - q[i]) for i in range(6)])
        # print(s, self.q)
        # print(self.q)
        # print(sum([abs(self.q[i] - q[i]) for i in range(6)]))
        # print(sum([abs(self.q[i] - q[i]) for i in range(6)]))
        # print('-> ', sae(q, self.q))
        err = sae(q, self.q)
        return err < 0.006 or (err < 0.025 and self.stopped_steps >= 30)
        # def similar_q(q1, q2):
        #     print(sum([abs(q1[i] - q2[i]) for i in range(len(q1))]))
        # return sum([abs(q1[i] - q2[i]) for i in range(len(q1))]) < 0.05
        #
        # at = self.at()
        # if self.last_query_position is not None:
        #     if similar_q(q, self.last_query_position):
        #         self.at_target_hit_counter += 1
        #
        #         if self.at_target_hit_counter > 30:
        #             self.last_query_position = None
        #             self.at_target_hit_counter = 0
        #             return True
        #
        #     else:
        #         self.last_query_position = None
        #         self.at_target_hit_counter = max(self.at_target_hit_counter, 0)
        #
        # self.last_query_position = at
        #
        # return False




@component(
    tag='ur5e',
    defaults={
        'interface_mjc': UR5eInterfaceMJC
    },
    template_path='ur5e.xml'
)
class UR5e:

    def __init__(self):
        pass

    def move_xyz(self, xyz=None, xyz_angles=None):
        pass

    def move_xyz_delta(self, xyz=None, xyz_angles=None):
        pass

    def move_q(self, args):
        pass

    def at(self):
        pass

    def at_xyz(self):
        pass

    def is_at(self):
        pass


class Behav:

    def __init__(self, pl: Platform, injector: Injector):
        self.pl = pl
        self.arm: UR5e = injector.get('ur5e')

    def on_update(self):
        q = [pi / 2, -pi / 2, pi / 2 - pi / 4, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))
        self.pl.wait_seconds(5)
        # self.gripper.move(0)

        q = [pi / 2, -pi / 2, pi / 2, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        # self.pl.wait(lambda: self.arm.is_at(q))
        self.pl.wait_seconds(5)

        # self.gripper.move(0.78)

        # self.pl.wait_seconds(10)
        self.pl.wait_seconds(5)

        q = [pi / 2, -pi / 2, pi / 2 - pi / 10, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait_seconds(5)
        # self.pl.wait(lambda: self.arm.is_at(q))

        q = [pi / 2, -pi / 2 + pi / 3, pi / 2 - pi / 10 + pi / 5, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait_seconds(5)
        # self.pl.wait(lambda: self.arm.is_at(q))

        # self.gripper.move(0.5)


def test():
    @component(
        components=[
            UR5e
        ],
        # language=xml
        template="""
                <mujoco>
                    <compiler angle="radian" meshdir="assets" autolimits="true" />

                    <worldbody>
                           <ur5e name='ur5e'/>
                    </worldbody>
                </mujoco>
            """
    )
    class UR5eTestWorld:
        pass

    conf = {
        'world': UR5eTestWorld,
        'behaviour': Behav,
        'defaults': {
            'environment': 'sim',
            'components': {
                '/gripper': {
                    'left_tip': False,
                    'right_tip': False,
                }
            },
            'plugins': [
                # (Cv2Inspector, {})
            ]
        },
        'environments': {
            'sim': {
                'platform': {
                    'class': PlatformMJC,
                    'width': 1000,
                    'height': 800,
                }
            }
        },
    }
    Platform.create(conf).run()


if __name__ == '__main__':
    test()
