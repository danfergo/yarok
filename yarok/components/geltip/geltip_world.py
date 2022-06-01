import yarok
from yarok.components_manager import component

from experimental_setup.components.geltip.geltip import GelTip


@component(
    components=[
        GelTip
    ],
    # language=xml
    template="""
        <mujoco>
            <visual>
                <!-- important for the Geltips, to ensure its camera frustum captures the close-up elastomer -->
                <map znear="0.001" zfar="50"/>
            </visual>
            
                <!-- <visual>
        <rgba haze="0.15 0.25 0.35 1"/>
        <quality shadowsize="2048"/>
        <map stiffness="700" shadowscale="0.5" fogstart="10" fogend="15" znear="0.001" zfar="40" haze="0"/>
    </visual> -->
            
                <!-- <default>
        <geom density="10"/>
    </default> -->

            <asset>
                <texture name="texplane" type="2d" builtin="checker" rgb1=".2 .3 .4" rgb2=".1 0.15 0.2"
                         width="512" height="512" mark="cross" markrgb=".8 .8 .8"/>    
                <material name="matplane" reflectance="0.3" texture="texplane" texrepeat="1 1" texuniform="true"/>
            </asset>
            <worldbody>
                <light directional="true" diffuse=".4 .4 .4" specular="0.1 0.1 0.1" pos="0 0 5.0" dir="0 0 -1"/>
                <light directional="true" diffuse=".6 .6 .6" specular="0.2 0.2 0.2" pos="0 0 4" dir="0 0 -1"/>
        
                <body name="floor">
                    <geom name="ground" type="plane" size="0 0 1" pos="0 0 0" quat="1 0 0 0" material="matplane" condim="1"/>
                </body>

                <body>
                    <geltip name="geltip1"/>
                    <body>
                      <!--  <geom pos=".009 -.009 .045" size=".0035" rgba="0 1 0 1"/> -->
                        <geom pos=".009 -.006 .03" size=".0025" rgba="0 1 0 1"/>
                    </body>
                </body>
        

                <body pos="0.05 0.05 0"> 
                    <geltip name="geltip2"/>
                    <body>
                        <!-- <geom pos=".009 -.009 .045" size=".0035" rgba="0 1 0 1"/> -->
                         <geom pos=".009 -.007 .03" size=".0035" rgba="0 1 1 1"/>
                    </body>
                </body>
                
                <body pos="0.1 0.1 0"> 
                    <geltip name="geltip3"/>
                    <body>
                        <!-- <geom pos=".009 -.009 .045" size=".0035" rgba="0 1 0 1"/> -->
                         <geom pos=".009 -.008 .03" size=".0055" rgba="1 0 0 1"/>
                    </body>
                </body>
                
                <body pos="0.3 0.3 0"> 
                    <geltip name="geltip444"/>
                    <body>
                        <!-- <geom pos=".009 -.009 .045" size=".0035" rgba="0 1 0 1"/> -->
                         <geom pos=".009 -.009 .03" size=".0065" rgba="1 0 0 1"/>
                    </body>
                </body>
                
                 <!-- <camera name="another_camera"  pos="0 0 0.5" mode="fixed" zaxis="0 0 1"/> -->
                <camera name="extrinsic_cam" pos="0 0 0.5" zaxis="0 0 1"/>
                
            </worldbody>        
        </mujoco>
    """
)
class GeltipWorld:

    def __init__(self, geltip1: GelTip):
        self.geltip1 = geltip1


if __name__ == '__main__':
    import sys

    yarok.run(GeltipWorld,
              None,
              {
                  'platform_args': {
                      'viewer_mode': sys.argv[1]
                  }
              })
