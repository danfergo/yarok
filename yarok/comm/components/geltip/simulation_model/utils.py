import numpy as np


# img utils

def normalize(img):
    img1 = img - np.min(img)
    mx = np.max(img1)
    if mx < 1e-4:
        return img1
    return img1 / mx


def normalize_vectors(m, zero=1.e-8):
    n = np.sqrt(np.sum(np.square(m), axis=2))
    n = np.where(((-1 * zero) < n) & (n < zero), 1, n)
    n = n[:, :, np.newaxis].repeat(3, axis=2)
    return m / n


"""
    Trimesh drawing utils
"""

from trimesh.geometry import align_vectors
from trimesh.transformations import translation_matrix
from trimesh.creation import cone, cylinder
from trimesh.primitives import Sphere

colors = {
    'green': [0, 255, 0, 255],
    'blue': [0, 0, 255, 255],
    'red': [255, 0, 0, 255],
    'pink': [255, 0, 255, 255],
    'yellow': [255, 255, 0, 255],
    'black': [0, 0, 0, 255],
}


def arrow(p, v, color='red', scale=0.25, length=0.25):
    r = align_vectors(
        np.array([0, 0, 1]),
        v,
        return_angle=False
    )

    trans = translation_matrix(p)
    transform = np.matmul(trans, r)
    h = cone(height=0.004 * length, radius=0.002 * scale, transform=transform)
    h.visual.face_colors = colors[color]

    t = cylinder(height=0.004 * scale, radius=0.001 * scale, transform=transform)

    t.visual.face_colors = [0, 0, 0, 255]

    return [h, t]


def sphere(pt):
    s = Sphere(radius=0.0002, center=pt, subdivisions=1)
    s.visual.face_colors = [0, 255, 0, 255]
    return s
