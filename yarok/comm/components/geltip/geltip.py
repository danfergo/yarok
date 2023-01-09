from yarok import component, interface, ConfigBlock
from yarok.platforms.mjc import InterfaceMJC

import numpy as np
import cv2
import os
import open3d as o3d

import math

from time import time

from .sim_model.model import SimulationModel
from .sim_model.utils.camera import circle_mask


@interface(
    defaults={
        'frame_size': (320, 240),
    }
)
class GelTipInterfaceMJC:

    def __init__(self, interface_mjc: InterfaceMJC, config: ConfigBlock):
        self.interface = interface_mjc
        self.frame_size = config['frame_size']
        self.mask = circle_mask(self.frame_size)
        bkg_zeros = np.zeros(self.frame_size[::-1] + (3,), dtype=np.float32)

        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        assets_path = os.path.join(__location__, './sim_model/assets/')

        elastic_deformation = True
        cloud, geodesic_light_fields = SimulationModel.load_assets(
            assets_path,
            (160, 120),
            self.frame_size,
            'geodesic',
            3)

        light_coeffs = [
            {'color': [196, 94, 255], 'id': 0.5, 'is': 0.1},  # red # [108, 82, 255]
            {'color': [154, 144, 255], 'id': 0.5, 'is': 0.1},  # green # [255, 130, 115]
            {'color': [104, 175, 255], 'id': 0.5, 'is': 0.1},  # blue  # [120, 255, 153]
        ]

        light_fiels = [{'field': geodesic_light_fields[l], **light_coeffs[l]} for l in range(3)]

        self.model = SimulationModel(**{
            'ia': 0.8,
            'light_sources': light_fiels,
            'background_depth': cv2.resize(np.load(assets_path + 'bkg.npy'), self.frame_size),
            'cloud_map': cloud,
            'background_img': bkg_zeros,  # bkg_rgb if use_bkg_rgb else
            'elastomer_thickness': 0.004,
            'min_depth': 0.026,
            'texture_sigma': 0.000005,
            'elastic_deformation': elastic_deformation
        })
        self.depth = np.zeros(self.frame_size, np.float32)

        self.last_update = 0

    def read(self):
        t = time()
        if self.last_update > t - 1.0:
            return self.tactile
        self.last_update = t
        shape = self.frame_size[1], self.frame_size[0]
        self.depth = self.interface.read_camera('camera', shape, depth=True, rgb=False)
        self.tactile = self.model.generate(self.depth).astype(np.uint8)
        return self.tactile

    def read_depth(self):
        return self.depth


class GelTipInterfaceHW:

    def __init__(self, config: ConfigBlock):
        self.cap = cv2.VideoCapture(config['cam_id'])
        if not self.cap.isOpened():
            raise Exception('GelTip cam ' + str(config['cam_id']) + ' not found')

        self.fake_depth = np.zeros((640, 480), np.float32)

    def read(self):
        [self.cap.read() for _ in range(10)]  # skip frames in the buffer.
        ret, frame = self.cap.read()
        return frame

    def read_depth(self):
        return self.fake_depth


@component(
    tag="geltip",
    defaults={
        'interface_mjc': GelTipInterfaceMJC,
        'interface_hw': GelTipInterfaceHW,
        'probe': lambda c: {'camera': c.read()},
        # template configs,
        'label_color': '255 0 0'
    },
    # language=xml
    template="""
        <mujoco>
            <asset>
                <material name="glass_material" rgba="1 1 1 0.1"/>
                <material name="white_elastomer" rgba="1 1 1 1"/>
                <material name="black_plastic" rgba=".3 .3 .3 1"/>
                
                <material name="label_color" rgba="${label_color} 1.0"/>
        
                <mesh name="geltip_shell" file="meshes/shell_open.stl" scale="0.001 0.001 0.001"/>
                <mesh name="geltip_sleeve" file="meshes/sleeve_open.stl" scale="0.001 0.001 0.001"/>
                <mesh name="geltip_mount" file="meshes/mount.stl" scale="0.001 0.001 0.001"/>
                
                <!-- the glass -->
                <mesh name="geltip_glass" file="meshes/glass_long.stl" scale="0.00099 0.00099 0.00099"/>
                
                <!-- the outter elastomer, for visual purposes -->
                <mesh name="geltip_elastomer" file="meshes/elastomer_long.stl" scale="0.0011 0.0011 0.0011"/>  
                
                <!-- inverted mesh, for limiting the depth map-->
                <!-- changing this mesh changes the depth maps -->
                <mesh name="geltip_elastomer_inv" file="meshes/elastomer_long_inv.stl" scale="0.00105 0.00105 0.00105"/>
        
            </asset>
            <worldbody>
                <body name="geltip">
                    <geom type="sphere" 
                        density="0.1"
                        material="label_color" 
                        size="0.005" 
                        pos="0.0 0.012 -0.025"/>
                    <geom density="0.1" type="mesh" mesh="geltip_shell" material="black_plastic"/>
                    <geom density="0.1" type="mesh" mesh="geltip_sleeve" material="black_plastic"/>
                    <geom density="0.1" type="mesh" mesh="geltip_mount" material="black_plastic"/>
                    <camera name="camera" pos="0 0 0.01" zaxis="0 0 -1" fovy="70"/>
                    <body>
                    
                       <!-- mesh, to serve as the glass and detect collisions -->
                             <!-- solimp="1.0 1.2 0.001 0.5 2" 
                              solref="0.02 1"-->
                       <geom density="0.1" type="mesh" 
                              mesh="geltip_glass" 
                              pos="0.0 0.0 -0.003"
                              friction="1 0.05 0.01" 
                              solimp="1.1 1.2 0.001 0.5 2" solref="0.02 1"
                              material="glass_material" /> 
                              
                       <!-- inverted, mesh, for limiting the depth-map -->
                       <!-- changing this geom/mesh changes the depth maps -->
                       <!-- 32 for contype and conaffinity disable collisions -->     
                       <geom  type="mesh" 
                              mesh="geltip_elastomer_inv" 
                              contype="32"  
                              conaffinity="32" 
                              pos="0.0 0.0 -0.005"
                              material="white_elastomer" />
                       
                       <!-- white elastomer, for visual purposes -->
                       <geom density="0.1" 
                              type="mesh" 
                              mesh="geltip_elastomer" 
                              friction="1 0.05 0.01" 
                              contype="32" 
                              conaffinity="32" 
                              pos="0.0 0.0 -0.007"
                              material="white_elastomer"/>
                    </body>
        
                </body>
            </worldbody>
        </mujoco>
    """
)
class GelTip:

    def __init__(self):
        """
            Geltip driver as proposed in
            https://danfergo.github.io/geltip-simulation/

            The frame method gets the depth map from the simula
        """
        pass

    def read(self):
        pass

    def read_depth(self):
        pass
