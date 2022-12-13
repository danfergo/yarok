from yarok import Platform, PlatformMJC, PlatformHW, component, ConfigBlock, Injector

from yarok.comm.worlds.empty_world import EmptyWorld
from yarok.comm.components.robotiq_2f85.robotiq_2f85 import Robotiq2f85
from yarok.comm.components.ur5.ur5 import UR5
from yarok.comm.components.digit.digit import Digit

from yarok.comm.plugins.cv2_inspector import Cv2Inspector
from yarok.comm.plugins.cv2_waitkey import Cv2WaitKey

from math import pi

import cv2


@component(
    extends=EmptyWorld,
    components=[
        UR5,
        Robotiq2f85,
        Digit
    ],
    # language=xml
    template="""
        <mujoco>
            <worldbody>
                

                
                <body>
                    <geom type="box" zaxis="1 1 1" size="0.01 0.01 0.01" pos="0.025 0.003 0.137"/>
                </body>

<!--                <ur5 name="arm"> -->
                   <robotiq_2f85 name="gripper" parent="ee_link">
                        <body xyaxes="0 -1 0 0 0 1" pos="0.0765 0.161 0.092" parent='right_tip'>
                            <digit name="digit1" />
                        </body>
                        <body xyaxes="0 -1 0 0 0 -1" pos="-0.0765 0.161 0.092" parent='left_tip'>
                            <digit name="digit2"/>
                        </body> 
                    </robotiq_2f85>
              <!--  </ur5>  -->
            </worldbody>        
        </mujoco>
    """
)
class DigitUR5World:
    pass


class DigitPickAndPlace:

    def __init__(self, pl: Platform, injector: Injector):
        # self.arm: UR5 = injector.get('arm')
        self.gripper = injector.get('gripper')
        self.pl = pl

    def on_update(self):
        self.gripper.move(0)
        self.gripper.move(1)


conf = {
    'world': DigitUR5World,
    'behaviour': DigitPickAndPlace,
    'defaults': {
        'environment': 'sim',
        'components': {
            '/gripper': {
                'left_tip': False,
                'right_tip': False,
            }
        },
        'plugins': [
            (Cv2Inspector, {})
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

if __name__ == '__main__':
    Platform.create(conf).run()
