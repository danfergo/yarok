from yarok import Platform, PlatformMJC, component, Injector

from yarok.comm.worlds.empty_world import EmptyWorld
from yarok.comm.components.robotiq_2f85.robotiq_2f85 import Robotiq2f85
from yarok.comm.components.ur5e.ur5e import UR5e
from yarok.comm.components.digit.digit import Digit

from yarok.comm.plugins.cv2_inspector import Cv2Inspector

from math import pi


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
            <worldbody>
               <!--
                <body>
                    <geom type="box" zaxis="1 1 1" size="0.01 0.01 0.01" pos="0.025 0.003 0.157"/>
                    <geom type="box" zaxis="-1 -1 -1" size="0.01 0.01 0.01" pos="-0.03 0.003 0.157"/>
                </body> -->
                <body pos='0 0 0.2'>
                    <freejoint/>
                    <geom type='cylinder' size='0.02 0.11' pos='-0.135 -0.48 0.11' mass='0.0001' zaxis='1 0 0'/>
                </body>
                <body>
                    <geom type="box" size="0.02 0.1 0.09" pos="-0.2 -0.48 0.09"/>
                    <geom type="box" size="0.02 0.1 0.09" pos="-0.05 -0.48 0.09"/>
                    <geom type="box" size="0.01 0.01 0.13" pos="-0.18 -0.44 0.13"/>
                    <geom type="box" size="0.01 0.01 0.13" pos="-0.18 -0.52 0.13"/>
                    <geom type="box" size="0.01 0.01 0.13" pos="-0.07 -0.52 0.13"/>
                    <geom type="box" size="0.01 0.01 0.13" pos="-0.07 -0.44 0.13"/>
                </body>
            <!-- body wrapper alignment for "old" gripper 
                right: xyaxes="0 -1 0 0 0 1" pos="0.0765 0.161 0.092" 
                left: xyaxes="0 -1 0 0 0 -1" pos="-0.0765 0.161 0.092"
            -->
                <ur5e name='arm'> 
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
class DigitUR5World:
    pass


class DigitPickAndPlace:

    def __init__(self, pl: Platform, injector: Injector):
        self.arm: UR5e = injector.get('arm')
        self.gripper = injector.get('gripper')
        self.pl = pl

    def on_update(self):
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
        self.pl.wait_seconds(3)

        self.pl.wait_seconds(5)
        self.gripper.move(140)
        # self.pl.wait(lambda: self.gripper.is_at(200))
        self.pl.wait_seconds(3)

        q = [0, -pi / 2, - pi / 2 - pi / 10 + pi / 5, -pi / 2 + pi / 10 - pi / 5, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))

        q = [0, -pi / 2, -pi / 2 + pi / 4, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.pl.wait(lambda: self.arm.is_at(q))

        # self.gripper.move(0.5)

        # print('open')
        # self.gripper.move(0)
        # self.pl.wait_seconds(5)
        # print('close')
        # self.gripper.move(1)
        # self.pl.wait_seconds(5)


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
