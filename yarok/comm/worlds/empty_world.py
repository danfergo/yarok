import yarok
from yarok import Platform, PlatformMJC, PlatformHW, component, ConfigBlock, Injector

@component(
    template="""
        <mujoco>
            <!-- possibly the physics solver -->
            <compiler angle="radian"  autolimits="true"/>
 <!--             <option impratio="10"/>

            <option timestep="0.01" solver="Newton" iterations="30" tolerance="1e-10" jacobian="auto" cone="pyramidal"/> -->
            <size nconmax="10000" njmax="10000"/>
            <visual>
                <!-- important for tactile sensors, to ensure the its camera frustum captures the close-up elastomer -->
                <map znear="0.001" zfar="100"/>
<!--                <quality shadowsize="2048"/> -->
            </visual>

            <asset>
                <!-- empty world -->
                <texture name="texplane" type="2d" builtin="checker" rgb1=".2 .3 .4" rgb2=".1 0.15 0.2"
                         width="512" height="512" mark="cross" markrgb=".8 .8 .8"/>    
                <material name="matplane" reflectance="0.3" texture="texplane" texrepeat="1 1" texuniform="true"/>
            </asset>

            <worldbody>
                <light directional="true" diffuse="1.0 1.0 1.0" specular="0.1 0.1 0.1" pos="0 0 5.0" dir="0 0 -1"/>
                <body name="floor">
                    <geom name="ground" type="plane" size="0 0 1" pos="0 0 0" quat="1 0 0 0" material="matplane"/>
                </body>
            </worldbody>

        </mujoco>
    """
)
class EmptyWorld:
    pass
