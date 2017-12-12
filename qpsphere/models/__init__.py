import numpy as np

from .mod_mie import mie
from .mod_proj import projection


available = {"mie": mie,
             "projection": projection,
             }


def simulate(radius=5e-6, sphere_index=1.339, medium_index=1.333,
             wavelength=550e-9, grid_size=(80, 80), model="projection",
             pixel_size=None, center=None):
    """Simulate scattering at a sphere

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
    grid_size: tuple of floats
        Resulting image size in x and y [px]
    model: str
        Sphere model to use (see `available`)
    pixel_size: float or None
        Pixel size [m]; if set to `None` the pixel size is
        chosen such that the radius fits at least three times
        into the grid.
    center: tuple of floats or None
        Center position in image coordinates [px]; if set to
        None, the center of the image (grid_size - 1)/2 is
        used.

    Returns
    -------
    qpi: qpimage.QPImage
        Quantitative phase data set
    """
    if pixel_size is None:
        pixel_size = 3 * radius / np.min(grid_size)

    if center is None:
        center = (np.array(grid_size) - 1) / 2

    model = available[model]
    qpi = model(radius=radius,
                sphere_index=sphere_index,
                medium_index=medium_index,
                wavelength=wavelength,
                pixel_size=pixel_size,
                grid_size=grid_size,
                center=center)
    return qpi
