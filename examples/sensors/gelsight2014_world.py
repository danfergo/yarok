from yarok.components_manager import component
from yarok.components.gelsight.gelsight2014 import gelsight2014

from yarok.mjc.platform import PlatformMJC
from yarok.hw.platform import PlatformHW

@component(
    # probe=lambda c: {'gelsight', c.gelsight.read()},
    components=[
        gelsight2014
    ],
    # language=xml
    template="""
    
    <mujoco>
        <visual>
            <!-- important for the GelSights' to ensure the camera's frustum captures the close-up elastomer -->
            <map znear="0.001" zfar="50"/>
        </visual>
    
        <asset>
            <!-- assets for the empty environment -->
            <texture name="texplane" type="2d" builtin="checker" rgb1=".2 .3 .4" rgb2=".1 0.15 0.2"
                     width="512" height="512" mark="cross" markrgb=".8 .8 .8"/>
            <material name="matplane" reflectance="0.3" texture="texplane" texrepeat="1 1" texuniform="true"/>
        </asset>
    
    
        <worldbody>
            <!-- empty environment geometries, lights, default camera (for the viewer) -->
            <camera name="viewer" pos="0 0 0.5" mode="fixed" zaxis="0 0 1"/>
            <light directional="true" diffuse=".4 .4 .4" specular="0.1 0.1 0.1" pos="0 0 5.0" dir="0 0 -1"/>
            <light directional="true" diffuse=".6 .6 .6" specular="0.2 0.2 0.2" pos="0 0 4" dir="0 0 -1"/>
            <body name="floor">
                <geom name="ground" type="plane" size="0 0 2" material="matplane" condim="1"/>
            </body>
    
    
            <!-- the gelsight -->
            <gelsight2014 name="gelsight1"/>
    
            <body>
                <geom name="sphere" pos=".0 .0 .035" size=".0035" rgba="0 1 0 1"/>
            </body>
    
        </worldbody>
    
    </mujoco>
    """
)
class Gelsight2014World:

    def __init__(self, gelsight2014: gelsight2014):
        self.gelsight2014 = gelsight2014


if __name__ == '__main__':
    import yarok
    import sys

    # yarok.run(PickAndPlaceWorld,
    #           PickAndPlaceBehaviour,
    #           {
    #               'platform_args': {
    #                   'viewer_mode': sys.argv[1]
    #               }
    #           })

    yarok.run({
        'world': Gelsight2014World,
        'defaults': {
            'environment': 'sim',
            'behaviour': {
            },
            'components': {
                '/': {
                    'object': 'cone'
                }
            }
        },
        'environments': {
            'sim': {
                'platform': {
                    'class': PlatformMJC,
                    'mode': 'view'
                },
                'inspector': True,
                'behaviour': {
                    'dataset_name': 'sim_depth'
                }
            },
            'real': {
                'platform': PlatformHW,
                'behaviour': {
                    'dataset_name': 'real_rgb'
                },
            }
        }
    })
