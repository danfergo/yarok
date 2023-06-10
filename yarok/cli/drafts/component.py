from yarok import ConfigBlock, component, interface
from yarok.platforms.mjc import InterfaceMJC


@interface()
class ComponentInterfaceMJC:
    def __init__(self, interface: InterfaceMJC):
        self.interface = interface


@component(
    tag='some_component',
    components=[],
    defaults={
        'mjc_interface': ComponentInterfaceMJC
    },
    # language=xml
    template="""
        <mujoco>
            <worldbody>

            </worldbody>
        </mujoco>
    """
)
class SomeComponent:
    pass