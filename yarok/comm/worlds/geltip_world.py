from yarok import Platform, PlatformMJC, PlatformHW, component, ConfigBlock, Injector

from yarok.comm.worlds.empty_world import EmptyWorld
from yarok.comm.components.robotiq_2f85.robotiq_2f85 import Robotiq2f85
from yarok.comm.components.ur5.ur5 import UR5
from yarok.comm.components.geltip.geltip import GelTip

from yarok.comm.plugins.cv2_inspector import Cv2Inspector
from yarok.comm.plugins.cv2_waitkey import Cv2WaitKey

from math import pi

import cv2

@component(
    extends=EmptyWorld,
    components=[
        UR5,
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

                <ur5 name="arm">
                   <robotiq_2f85 name="gripper" parent="ee_link">
                        <!-- <body pos="0 0.02 0.0395" parent="right_tip">
                            <geltip name="geltip1" parent="left_tip"/>
                        </body>
                        <body pos="0 0.02 0.0395" parent="left_tip">
                            <geltip name="geltip2" parent="right_tip"/>
                        </body> -->
                    </robotiq_2f85>
                </ur5> 
            </worldbody>        
        </mujoco>
    """
)
class GraspRopeWorld:
    pass


class GraspRoleBehaviour:

    def __init__(self, arm: UR5, gripper: Robotiq2f85, pl: Platform, injector: Injector):
        self.arm: UR5 = injector.get('arm')
        self.gripper = gripper
        self.pl = pl

    def on_update(self):
        q = [pi / 2, -pi / 2, pi / 2 - pi / 4, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.gripper.move(0)
        self.pl.wait(lambda: self.arm.is_at(q) and self.gripper.is_at(0))

        q = [pi / 2, -pi / 2, pi / 2, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))

        self.gripper.move(0.78)

        # self.pl.wait_seconds(10)

        q = [pi / 2, -pi / 2, pi / 2 - pi / 10, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))

        q = [pi / 2, -pi / 2 + pi / 3, pi / 2 - pi / 10 + pi / 5, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))

        self.gripper.move(0.5)


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
                (Cv2WaitKey, {'ms': 10})
            ]
        }
    },
}

if __name__ == '__main__':
    Platform.create(conf).run()
