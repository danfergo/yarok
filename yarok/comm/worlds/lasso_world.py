from yarok import Platform, PlatformMJC, component, Injector

from yarok.comm.worlds.empty_world import EmptyWorld
from yarok.comm.components.robotiq_2f85.robotiq_2f85 import Robotiq2f85
from yarok.comm.components.geltip.geltip import GelTip
from yarok.comm.components.ur5e.ur5e import UR5e

from math import pi

import cv2

from math import sin, cos


@component(
    extends=EmptyWorld,
    components=[
        UR5e,
        Robotiq2f85,
        GelTip
    ],
    # language=xml
    template="""
        <mujoco>
            <worldbody>
                
                <body pos="0.5 -0.1 -0.63"> 
                    <composite type="grid" count="40 1 1" spacing="0.01" offset="0 0 1">
                        <!-- <skin material="matplane" inflate="0.001" subgrid="3" texcoord="true"/> -->
                        <joint kind="main" damping="0.01"/>
                        <tendon kind="main" width="0.01" rgba=".8 .2 .1 1"/>
                        <geom size=".01" rgba=".8 .2 .1 1"/>
                        <!-- <pin coord="1"/> -->
                        <pin coord="39"/> 
                    </composite>
                </body>
                
                <body>
                    <geom type="box" size="0.01 0.1 0.12" pos="0.4 -0.05 0.12"/>
                </body>
                <body pos='0 0 0.5'>
                    <ur5e name="arm">
                        <robotiq-2f85 name="gripper" parent="ee_link"> 
                            <!-- <body pos="0 0.02 0.0395" parent="right_tip">
                                <geltip name="geltip1" parent="left_tip"/>
                            </body>
                            <body pos="0 0.02 0.0395" parent="left_tip">
                                <geltip name="geltip2" parent="right_tip"/>
                            </body> -->
                        </robotiq-2f85> 
                    </ur5e> 
                </body>
            </worldbody>        
        </mujoco>
    """
)
class GraspRopeWorld:
    pass


class GraspRoleBehaviour:

    def __init__(self, pl: Platform, injector: Injector):
        self.arm: UR5e = injector.get('arm')
        self.gripper = None
        self.pl = pl

    def on_start(self):
        print('START WORLD!')

    def on_update(self):
        # self.arm.move_q([0, 0, 0, -pi / 2, -pi / 2, 0])
        # self.pl.wait_seconds(15)

        # print(self.arm.at_xyz())
        #
        # self.pl.wait(
        #     self.arm.move_xyz(xyz_angles=[pi/2, 0, 0])
        # )
        # self.pl.wait_seconds(10)
        # print([3.11700289e+00, - 1.62981294e-07,  1.57079633e+00], )
        self.pl.wait(
            self.arm.move_xyz(xyz=[0.35, 0.35, 0.7], xyz_angles=[0, 0.1, pi])
        )

        # https://flexbooks.ck12.org/cbook/ck-12-precalculus-concepts-2.0/section/10.3/related/lesson/parametric-equations-for-circles-and-ellipses-calc/
        a = 0.6
        b = 0.6
        x = lambda t: a * cos(t)
        y = lambda t: b * sin(t)

        alpha = pi / 4
        while True:
            # print('t', t)
            alpha += 0.1
            self.pl.wait(
                self.arm.move_xyz(xyz=[x(alpha), y(alpha), 0.7], xyz_angles=[0, 0.1, alpha])
            )
            # if alpha >= 2 * pi:
            #     alpha = 0
        self.pl.wait_seconds(1000)

        # for i in range(10):
        #     for j in range(10):
        #         self.pl.wait(
        #             self.arm.move_xyz(xyz=[0.35 + 0.01*i, 0.35+0.01*j, 0.1], xyz_angles=[3.11, -1.6e-7, -pi / 2])
        #         )
        #         self.pl.wait_seconds(1)

        print('ended', self.arm.at())

        # for i in range(10):
        #     print('...')
        #     print(self.arm.at_xyz()[0])
        #     self.pl.wait(
        #         self.arm.move_xyz_delta(xyz=[0.01, 0, 0])
        #     )
        # self.arm.move_xyz(xyz=[-0.90966839 + 0.01*i, -0.10914999, -0.01239996],
        #                   xyz_angles=[3.11700289e+00, -1.62981294e-07, 1.57079633e+00])
        # self.pl.wait_seconds(1)

        # print('=======')
        # print('=======')
        # print('=======')

        self.pl.wait_seconds(1000)
        pass

        q = [pi / 2, -pi / 2, -pi / 2 + pi / 4, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        # self.gripper.move(0)
        # and self.gripper.is_at(0)
        self.pl.wait(lambda: self.arm.is_at(q))
        print('----')

        q = [pi / 2, -pi / 2, -pi / 2, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))
        print('----')

        # self.gripper.move(0.78)

        # self.pl.wait_seconds(10)

        q = [pi / 2, -pi / 2, - pi / 2 - pi / 10, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))

        q = [pi / 2, -pi / 2 + pi / 3, - pi / 2 - pi / 10 + pi / 5, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))

        # self.gripper.move(0.5)


conf = {
    'world': GraspRopeWorld,
    'behaviour': GraspRoleBehaviour,
    'defaults': {
        'environment': 'sim',
        'behaviour': {
        },
        'components': {
            '/': {
                'object': 'cone'
            },
            '/arm': {
                'speed': pi / 8
            },
            '/gripper': {
                # 'left_tip': False,
                # 'right_tip': False,
            }
        },
        'plugins': [
            # Cv2Inspector,
        ]
    },
    'environments': {
        'sim': {
            'platform': {
                'class': PlatformMJC,
                'width': 1200,
                'height': 800
            },
            'plugins': [
                # (Cv2WaitKey, {'ms': 1000})
            ]
        }
    },
}

if __name__ == '__main__':
    Platform.create(conf).run()
