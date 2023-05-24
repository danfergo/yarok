from yarok import component


@component(
    tag='bucket-particles',
    defaults={
        'pos': [-0.135, -0.52, 0.165]
    },
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
                    <body pos='${pos[0]} ${pos[1]} ${pos[2]+0.05}'>
                        <body zaxis='1 1 1'>
                            <composite type="particle" count="4 4 4" spacing="0.0125">
                                <geom size="0.008" material='red'/>
                            </composite>
                        </body>
                    </body>   
                    
                    <body pos='${pos[0]} ${pos[1]} ${pos[2]+2*0.05}'>
                 <!--   zaxis='1 1 1' -->
                        <body >
                            <composite type="particle" count="4 4 4" spacing="0.02">
                                <geom size="0.008" material='green' mass='0.0001'/>
                            </composite>
                        </body>
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
            </worldbody>
        </mujoco>
    """
)
class BucketParticles:

    def __init__(self):
        pass
