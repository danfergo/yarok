import mujoco
import cv2
import time
import numpy as np
# from gym.envs.mujoco.mujoco_rendering import RenderContextOffscreen
import os
from .utils.phong_render import PhongRender

gel_width, gel_height = 240,320

def get_simapproach():
    # load the image taken from a real digit sensor

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    model_path      = os.path.join(__location__, './assets/gel/digit_bg.npy')
    background_img  = np.load(model_path)
    # Phong render params
    ## sensor light sources
    light_sources_digit = [
        {'position': [-0.866, 0.5, 0.25], 'color': (108, 82, 255), 'kd': 0.1, 'ks': 0.4},  # red, bottom (108, 82, 255) kd0.6
        {'position': [0.866, 0.5, 0.25], 'color': (120, 255, 153), 'kd': 0.1, 'ks': 0.4},  # green, left (120, 255, 153)
        {'position': [0, -1, 0.25], 'color': (255, 130, 115), 'kd': 0.3, 'ks': 0.4},  # blue, left (255, 130, 115)
    ]

    ## calculation attributes
    ka                  = 1.0
    px2m_ratio          = 5.4347826087e-05
    elastomer_thickness = 1.0  
    min_depth           = 0 
    texture_sigma       = 0.00001 

    simulation = PhongRender(
        light_sources       = light_sources_digit,
        background_img      = background_img,
        ka                  = ka,
        texture_sigma       = texture_sigma,
        px2m_ratio          = px2m_ratio,
        elastomer_thickness = elastomer_thickness,
        min_depth           = min_depth,
    )

    return simulation

if __name__=="__main__":
    filepath = "digit.xml"

    model = mujoco.MjModel.from_xml_path(filepath)
    data = mujoco.MjData(model)
    viewer = RenderContextOffscreen(gel_width,gel_height,model,data)

    # while True:
    mujoco.mj_step(model,data)
    # obtain depth and mask
    viewer.render(gel_width,gel_height,camera_id=0)
    depth = viewer.read_pixels(gel_width, gel_height, depth=True)[1].copy()
    depth = np.fliplr(depth)

    # render depth to tactile img
    simulation = get_simapproach()
    tact_img = simulation.generate(depth)

    cv2.imshow("tactile_img", tact_img)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()