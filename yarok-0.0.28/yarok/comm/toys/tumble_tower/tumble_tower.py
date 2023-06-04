from yarok import component, interface


@component(
    tag='tumble-tower',
    defaults={
      'rows': 8
    },
    # language=xml
    template="""
        <mujoco>
            <asset>
                <material name="wood" rgba="0.5 0.4 0.3 1" specular="0.95"/>
            </asset>
            <default>
                <default class='tt-block'>
                    <geom type='box'
                     material='wood'
                            mass='0.1'
                            size="0.04 0.12 0.028"/>
                    
                </default>
            </default>
            <worldbody>
                <for each='range(rows)' as='z'>
                    <for each='range(3)' as='x'>
                        <body pos="
                                ${0.5 + 0.082*x if z % 2 == 0 else 0.58} 
                                ${0.48 if z % 2 == 0 else 0.4 + 0.082*x}
                                ${0.061*z}" 
                            euler="0 0 ${0 if z % 2 == 0 else 1.57}">
                            <freejoint/>
                            <geom class='tt-block'/>
                        </body>
                    </for>
                </for>
                <!--
            
                <body>
                    <geom class='tt-block-left'/>
                    <geom class='tt-block-center'/>
                    <geom class='tt-block-right'/>
                </body>
                
                <body euler='0 0 1.57' pos='0 0 0.061'>
                    <geom class='tt-block-left'/>
                    <geom class='tt-block-center'/>
                    <geom class='tt-block-right'/>
                </body>
                
                <body pos='0 0 0.121'>
                    <geom class='tt-block-left'/>
                    <geom class='tt-block-center'/>
                    <geom class='tt-block-right'/>
                </body>
                
                <body euler='0 0 1.57' pos='0 0 0.181'>
                    <geom class='tt-block-left'/>
                    <geom class='tt-block-center'/>
                    <geom class='tt-block-right'/>
                </body>
                
                <body pos='0 0 0.241'>
                    <geom class='tt-block-left'/>
                    <geom class='tt-block-center'/>
                    <geom class='tt-block-right'/>
                </body>
                
                <body euler='0 0 1.57' pos='0 0 0.301'>
                    <geom class='tt-block-left'/>
                    <geom class='tt-block-center'/>
                    <geom class='tt-block-right'/>
                </body>
                
                <body pos='0 0 0.361'>
                    <geom class='tt-block-left'/>
                    <geom class='tt-block-center'/>
                    <geom class='tt-block-right'/>
                </body>
                
                <body euler='0 0 1.57' pos='0 0 0.421'>
                    <geom class='tt-block-left'/>
                    <geom class='tt-block-center'/>
                    <geom class='tt-block-right'/>
                </body> -->
                
            </worldbody>
        </mujoco>
    """
)
class TumbleTower:
    pass


if __name__ == '__main__':
    from yarok import Platform, Injector
    from yarok.comm.worlds.empty_world import EmptyWorld
    from yarok.comm.components.ur5e.ur5e import UR5e
    from yarok.comm.components.robotiq_2f85.robotiq_2f85 import Robotiq2f85

    from math import pi

    @component(
        extends=EmptyWorld,
        components=[
            TumbleTower,
            UR5e,
            Robotiq2f85
        ],
        template="""
            <mujoco>
                <worldbody>
                    <tumble-tower name="tower"/>
                    
                    <body euler="0 0 1.57">
                        <ur5e name='arm'>
                           <robotiq-2f85 name="gripper" parent="ee_link"> 
                            </robotiq-2f85> 
                        </ur5e>
                    </body>
                </worldbody>
            </mujoco>
        """
    )
    class BlocksTowerTestWorld:
        pass


    class TumbleTheTowerBehaviour:

        def __init__(self, injector: Injector):
            self.arm: UR5e = injector.get('arm')
            self.pl: Platform = injector.get(Platform)

        def on_update(self):
            self.pl.wait_seconds(10)
            self.pl.wait(
                self.arm.move_xyz(xyz=[0.8, 0.1, 0.12], xyz_angles=[3.11, -1.6e-7, -pi / 2])
            )

            self.pl.wait(
                self.arm.move_xyz(xyz=[0.1, 0.8, 0.12], xyz_angles=[3.11, -1.6e-7, -pi / 2])
            )

            self.pl.wait_seconds(1000)


    Platform.create({
        'world': BlocksTowerTestWorld,
        'behaviour': TumbleTheTowerBehaviour,
        'defaults': {
            'plugins': []
        }
    }).run()
