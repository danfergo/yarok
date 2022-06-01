import yarok
from yarok.components_manager import component

from yarok.components.robotiq_2f85.robotiq_2f85 import robotiq_2f85
from yarok.components.ur5.ur5 import UR5

from yarok.components.geltip.geltip import GelTip

from yarok import wait
from math import pi


@component(
    components=[
        UR5,
        robotiq_2f85,
        GelTip
    ],
    # language=xml
    template="""
        <mujoco>
            <!-- possibly the physics solver -->
            <option timestep="0.01" solver="Newton" iterations="30" tolerance="1e-10" jacobian="auto" cone="pyramidal"/>
            <compiler angle="radian"/>

            <visual>
                <!-- important for the Geltips, to ensure the its camera frustum captures the close-up elastomer -->
                <map znear="0.001" zfar="50"/>
                <quality shadowsize="2048"/>
            </visual>

            <asset>
                <!-- empty world -->
                <texture name="texplane" type="2d" builtin="checker" rgb1=".2 .3 .4" rgb2=".1 0.15 0.2"
                         width="512" height="512" mark="cross" markrgb=".8 .8 .8"/>    
                <material name="matplane" reflectance="0.3" texture="texplane" texrepeat="1 1" texuniform="true"/>
            </asset>


            <worldbody>
                <light directional="true" diffuse=".4 .4 .4" specular="0.1 0.1 0.1" pos="0 0 5.0" dir="0 0 -1"/>
                <light directional="true" diffuse=".6 .6 .6" specular="0.2 0.2 0.2" pos="0 0 4" dir="0 0 -1"/>
                <camera name="viewer" pos="-0. -2 0.3" mode="fixed" zaxis="0 -1 0"/>

                <body name="floor">
                    <geom name="ground" type="plane" size="0 0 1" pos="0 0 0" quat="1 0 0 0" material="matplane" condim="1"/>
                </body>
  <!--              xyaxes="0 1 0 1 0 0" -->
                <body pos="0.5 -0.1 -0.63" > 
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
                        <body pos="0 0.02 0.0395" parent="right_tip">
                            <geltip name="geltip1" parent="left_tip"/>
                        </body>
                        <body pos="0 0.02 0.0395" parent="left_tip">
                            <geltip name="geltip2" parent="right_tip"/>
                           <!-- <body>
                                <geom pos=".009 -.009 .045" size=".0035" rgba="0 1 0 1"/>
                                <geom pos="-.009 .009 .03" size=".0035" rgba="0 1 0 1"/>
                            </body> -->
                        </body>
                    </robotiq_2f85>
                </ur5> 
            </worldbody>        
        </mujoco>
    """
)
class GraspRopeWorld:

    def __init__(self):
        pass
i = 0

class GraspRoleBehaviour:

    def __init__(self, arm: UR5, gripper: robotiq_2f85):
        self.arm = arm
        self.gripper = gripper

    def wake_up(self):
        q = [pi / 2, -pi / 2, pi / 2 - pi / 4, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        self.gripper.move(0)
        wait(lambda: self.arm.is_at(q) and self.gripper.is_at(0))

        q = [pi / 2, -pi / 2, pi / 2, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        wait(lambda: self.arm.is_at(q))

        self.gripper.move(0.75)

        def x():
            global i
            i += 1
            return i > 100
        wait(x)

        q = [pi / 2, -pi / 2, pi / 2 - pi / 10, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        wait(lambda: self.arm.is_at(q))

        q = [pi / 2, -pi / 2 + pi / 3, pi / 2 - pi / 10 + pi / 5, 0, pi / 2, pi / 2]
        self.arm.move_q(q)
        wait(lambda: self.arm.is_at(q))

        self.gripper.move(0.5)
