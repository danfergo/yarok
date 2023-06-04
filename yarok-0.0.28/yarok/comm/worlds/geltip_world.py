from yarok import Platform, PlatformMJC, PlatformHW, component, ConfigBlock, Injector

from yarok.comm.worlds.empty_world import EmptyWorld
from yarok.comm.components.robotiq_2f85.robotiq_2f85 import Robotiq2f85
from yarok.comm.components.ur5.ur5 import UR5
from yarok.comm.components.geltip.geltip import GelTip
from yarok.comm.components.ur5e.ur5e import UR5e
from yarok.comm.components.cam.cam import Cam

from yarok.comm.plugins.cv2_inspector import Cv2Inspector
from yarok.comm.plugins.cv2_waitkey import Cv2WaitKey

from math import pi

import cv2

@component(
    extends=EmptyWorld,
    components=[
        UR5e,
        Robotiq2f85,
        GelTip,
        Cam
    ],
    # language=xml
    template="""
        <mujoco>
            <default>
                <default class='marker'>
                    <geom type="box" 
                        size="0.02 0.02 0.001" 
                        conaffinity='32' 
                        contype='32'/>
                </default>
            </default>
            <worldbody>
                
                <body pos="0.5 0.5 0.4"> 
                    <composite type="grid" count="30 1 1" spacing="0.009" offset="0 0 1">
                        <!-- <skin material="matplane" inflate="0.001" subgrid="3" texcoord="true"/> -->
                        <joint kind="main" damping="0.001" frictionloss='0.0001'/>
                        <tendon kind="main" width="0.019" rgba=".8 .2 .1 1"/>
                        <geom size=".018" rgba=".8 .2 .1 1" mass='0.0001' 
                            friction='0.1 0.005 0.0001'/><!--
                            -->
                        <!-- <pin coord="1"/> -->
                        <!-- <pin coord="39"/> -->
                    </composite>
                </body>
                
                <body>
                    <geom type="box" size="1.0 1.0 0.05" pos="0 0 0.45"/>
                    <geom class="marker" pos="0.7 0.7 0.5" rgba='255 0 0 1'/>
                    <geom class="marker" pos="0.1 0.7 0.5" rgba='0 255 0 1'/>
                    <geom class="marker" pos="0.1 0.3 0.5" rgba='0 0 255 1'/>
                    <geom class="marker" pos="0.7 0.3 0.5" rgba='255 0 255 1'/>
                   <!-- <geom type="box" size=".025 .025 1.0" pos="1.0 1.0 1.0"/> -->
                </body>
                
                <body  pos='0.9 0.9 1' euler='1.6 2.35619449019 0'>
                   <body euler='2.35619449019 0 3.14159265359'>
                     <cam name='vis_cam'/>
                   </body>
                </body>
                
                <body pos='0 0 0.5' xyaxes='0 1 0 -1 0 0'>
                    <ur5e name="arm">
                       <robotiq-2f85 name="gripper" parent="ee_link"> 
                             <body pos="0.02 -0.017 0.053" xyaxes="0 -1 0 1 0 0" parent="right_tip">
                                <geltip name="right_geltip" parent="left_tip"/>
                            </body>
                           <body pos="-0.02 -0.017 0.053" xyaxes="0 1 0 -1 0 0" parent="left_tip">
                                <geltip name="left_geltip" parent="right_tip"/>
                            </body>
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
        self.gripper: Robotiq2f85 = injector.get('gripper')
        self.pl = pl

    def on_update(self):
        # self.pl.wait_seconds(60)
        # print('------------------------------------------------------------------------------------------->')

        self.gripper.close(0.5)

        self.pl.wait(
            self.arm.move_xyz(xyz=[0.45, 0.5, 0.2], xyz_angles=[3.11, -1.6e-7, -pi / 2])
        )

        self.pl.wait(
            self.arm.move_xyz(xyz=[0.45, 0.5, 0.17], xyz_angles=[3.11, -1.6e-7, -pi / 2])
        )
        self.pl.wait_seconds(2)
        self.pl.wait(
            self.gripper.close(0.75)
        )
        self.pl.wait_seconds(10)
        print('closed gripper')

        self.pl.wait(
            self.arm.move_xyz(xyz=[0.45, 0.5, 0.4], xyz_angles=[3.11, -1.6e-7, -pi / 2])
        )

        self.pl.wait(
            self.arm.move_xyz(xyz=[0.45, 0.2, 0.4], xyz_angles=[3.11, -1.6e-7, -pi / 2])
        )
        self.pl.wait(
            self.arm.move_xyz(xyz=[0.45, 0.2, 0.25], xyz_angles=[3.11, -1.6e-7, -pi / 2])
        )
        self.pl.wait(
            self.gripper.close(0.5)
        )


        print('ended.')
        self.pl.wait_seconds(100)


conf = {
    'world': GraspRopeWorld,
    'behaviour': GraspRoleBehaviour,
    'defaults': {
        'environment': 'sim',
        'behaviour': {
        },
        'components': {
            '/gripper': {
                'left_tip': False,
                'right_tip': False,
            },
            '/right_geltip': {
                'label_color': '255 0 0'
            },
            '/left_geltip': {
                'label_color': '0 255 0'
            },
        },
    },
    'environments': {
        'sim': {
            'platform': {
                'class': PlatformMJC,
                'width': 800,
                'height': 600
            },
            'plugins': [
                (Cv2Inspector, {})
            ]
        }
    },
}

if __name__ == '__main__':
    Platform.create(conf).run()
