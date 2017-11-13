import numpy as np
import qpimage


def projection(radius=5, sphere_index=1.339, medium_index=1.333,
               wavelength=550e-9, pixel_size=.1, grid_size=(80, 80),
               center=(40, 40)):
    """Optical path difference for a dielectric sphere

    Parameters
    ----------
    radius: float
        Radius of the sphere [m]
    sphere_index: float
        Refractive index of the object
    medium_index: float
        Refractive index of the surrounding medium
    wavelength: float
        Vacuum wavelength of the imaging light [m]
    pixel_size: float
        Pixel size [m]
    grid_size: tuple of floats
        Resulting image size in x and y [px]
    center: tuple of floats
        Center position in image coordinates [px]

    Returns
    -------
    qpi: qpimage.QPImage
        Quantitative phase data set
    """
    # grid
    x = np.arange(grid_size[0]).reshape(-1, 1)
    y = np.arange(grid_size[1]).reshape(1, -1)
    cx, cy = center
    # sphere location
    rpx = radius / pixel_size
    r = rpx**2 - (x - cx)**2 - (y - cy)**2
    # distance
    z = np.zeros_like(r)
    rvalid = r > 0
    z[rvalid] = 2 * np.sqrt(r[rvalid]) * pixel_size
    # phase = delta_n * 2PI * z / wavelength
    phase = (sphere_index - medium_index) * 2 * np.pi * z / wavelength
    meta_data = {"pixel size": pixel_size,
                 "wavelength": wavelength,
                 "medium index": medium_index,
                 "sim center": center,
                 "sim radius": radius,
                 "sim index": sphere_index,
                 }
    qpi = qpimage.QPImage(data=phase, which_data="phase",
                          meta_data=meta_data)
    return qpi
