import numpy as np
import scipy.ndimage.filters as fi
import cv2

def dot(a, b):
    return np.sum(np.multiply(a, b), axis=2)


def normalize_vectors(m, zero=1.e-9):
    n = np.sqrt(np.sum(np.square(m), axis=2))
    n = np.where(((-1 * zero) < n) & (n < zero), 1, n)
    n = n[:, :, np.newaxis].repeat(3, axis=2)
    return m / n


def derivative(mat, direction):
    assert (direction == 'x' or direction == 'y'), "The derivative direction must be 'x' or 'y'"
    kernel = None
    if direction == 'x':
        kernel = [[-1.0, 0.0, 1.0]]
    elif direction == 'y':
        kernel = [[-1.0], [0.0], [1.0]]
    kernel = np.array(kernel, dtype=np.float32)
    return cv2.filter2D(mat, -1, kernel) / 2.0


def gkern2(kernlen=21, nsig=3):
    """Returns a 2D Gaussian kernel array."""

    # create nxn zeros
    inp = np.zeros((kernlen, kernlen))
    # set element at the middle to one, a dirac delta
    inp[kernlen // 2, kernlen // 2] = 1
    # gaussian-smooth the dirac, resulting in a gaussian filter mask
    return fi.gaussian_filter(inp, nsig)

