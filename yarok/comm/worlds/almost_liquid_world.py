from yarok import Platform, PlatformMJC, PlatformHW, component, ConfigBlock, Injector

from yarok.comm.worlds.empty_world import EmptyWorld
from yarok.comm.components.robotiq_2f85.robotiq_2f85 import Robotiq2f85
from yarok.comm.components.ur5e.ur5e import UR5e
from yarok.comm.components.digit.digit import Digit

from yarok.comm.plugins.cv2_inspector import Cv2Inspector
from yarok.comm.plugins.cv2_waitkey import Cv2WaitKey

from math import pi

import cv2


@component(
    extends=EmptyWorld,
    components=[
        UR5e,
        Robotiq2f85,
        Digit
    ],
    # language=xml
    template="""
        <mujoco>
            <asset>
                <material name='glass' rgba='1 1 1 0.1'/>
                <material name='red' rgba='.8 .2 .1 1'/>
                <material name='green' rgba='.2 .8 .1 1'/>
            </asset>
            
            <default>
                <default class='cup_side'>
                    <geom type="box" 
                    material='glass' 
                    size="0.0025 0.0220 0.0500" 
                    pos="0.05 0.0 0.0500" 
                    euler='0 0.05 0'/>
                </default>
                <default class='cup_bottom'>
                    <geom type="box" material='glass' size="0.0220 0.0500 0.0025"/>
                </default>
            </default>
            
            <worldbody>
                
                <body pos='-0.135 -0.52 0.22'>
                    <body zaxis='1 1 1'>
                        <composite type="particle" count="4 4 4" spacing="0.0125">
                            <geom size="0.008" material='red'/>
                        </composite>
                    </body>
                </body>   
                
                <body pos='-0.135 -0.52 0.27'>
             <!--   zaxis='1 1 1' -->
                    <body >
                        <composite type="particle" count="4 4 4" spacing="0.02">
                            <geom size="0.008" material='green' mass='0.0001'/>
                        </composite>
                    </body>
                </body>               
             
             <body pos='-0.135 -0.48 0.016'>
                <geom type='box' size='0.2 0.2 0.14'/>
             </body>

                 <body pos='-0.135 -0.52 0.165'>
                    <freejoint/> 
                    <body euler='0 0 0.0'>
                        <geom class='cup_side'/>
                    </body>
                    <body euler='0 0 0.78539816339'>
                        <geom class='cup_side'/>
                    </body> 
                    <body euler='0 0 1.57079632679'>
                        <geom class='cup_side'/>
                    </body> 
                    <body euler='0 0 2.35619449019'>
                        <geom class='cup_side'/>
                    </body> 
                    <body euler='0 0 3.14159265359'>
                        <geom class='cup_side'/>
                    </body> 
                    <body euler='0 0 0.78539816339'>
                        <geom class='cup_side'/>
                    </body> 
                    <body euler='0 0 3.92699081699'>
                        <geom class='cup_side'/>
                    </body> 
                    <body euler='0 0 4.71238898038'>
                        <geom class='cup_side'/>
                    </body> 
                    <body euler='0 0 5.49778714378'>
                        <geom class='cup_side'/>
                    </body> 
                    
                    <body>
                        <geom class='cup_bottom' euler='0 0 -0.78539816339'/>
                        <geom class='cup_bottom' euler='0 0 0'/>
                        <geom class='cup_bottom' euler='0 0 0.78539816339'/>
                        <geom class='cup_bottom' euler='0 0 1.57079632679'/>
                    </body> 
                </body>
                

                <ur5e name="arm"> 
                   <robotiq-2f85 name="gripper" parent="ee_link"> 
                        <body xyaxes='0 0 -1 1 0 0' pos="-0.001  0.009 .064" parent='right_tip'>
                            <digit name="digit1" />
                        </body>
                        <body xyaxes='0 0 -1 1 0 0' pos="-0.001  0.009 .064" parent='left_tip'>
                            <digit name="digit2" />
                        </body>
                    </robotiq-2f85> 
                </ur5e>  
            </worldbody>        
        </mujoco>
    """
)
class AlmostLiquidWorld:
    pass


class AlmostLiquidPouringBehaviour:

    def __init__(self, pl: Platform, injector: Injector):
        self.arm: UR5 = injector.get('arm')
        self.gripper = injector.get('gripper')
        self.pl = pl

    def on_update(self):
        self.pl.wait_seconds(60)
        print('------------------------------------------------------------------------------------------->')


        q = [0, -pi / 2, -pi / 2 + pi / 4, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.gripper.move(0)
        self.pl.wait(lambda: self.arm.is_at(q) and self.gripper.is_at(0))
        print('----')

        q = [0, -pi / 2, -pi / 2, -pi / 2, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))
        print('----')

        # self.gripper.move(0.78)

        # self.pl.wait_seconds(10)

        q = [0, -pi / 2, - pi / 2 - pi / 10, -pi / 2 + pi / 10, pi / 2, pi / 2]
        self.arm.move_q(q)

        self.pl.wait(lambda: self.arm.is_at(q))
        self.pl.wait_seconds(30)



conf = {
    'world': AlmostLiquidWorld,
    'behaviour': AlmostLiquidPouringBehaviour,
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
