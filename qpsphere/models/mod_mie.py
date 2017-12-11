import numpy as np
import qpimage

from ._bhfield import simulate_sphere


def mie(radius=5, sphere_index=1.339, medium_index=1.333,
        wavelength=550e-9, pixel_size=.1, grid_size=(80, 80),
        center=(40, 40), arp=True):
    """Mie-simulated field behind a dielectric sphere (BHFIELD)

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
    arp: bool
        Use arbitrary precision (ARPREC) in BHFIELD computations

    Returns
    -------
    qpi: qpimage.QPImage
        Quantitative phase data set
    """
    # simulation parameters
    radius_um = radius * 1e6  # radius of sphere in um
    propd_um = radius_um  # simulate propagation through full sphere
    propd_lamd = radius / wavelength  # radius in wavelengths
    size_um = np.array(grid_size) * pixel_size * 1e6
    wave_nm = wavelength * 1e9

    kwargs = {"radius_sphere_um": radius_um,
              "refractive_index_medium": medium_index,
              "refractive_index_sphere": sphere_index,
              "measurement_position_um": propd_um,
              "wavelength_nm": wave_nm,
              "size_simulation_um": size_um,
              "size_grid": grid_size,
              "offset_x_um": center[0],
              "offset_y_um": center[1]}

    background = np.exp(1j * 2 * np.pi * propd_lamd * medium_index)

    field = simulate_sphere(arp=arp, **kwargs) / background

    meta_data = {"pixel size": pixel_size,
                 "wavelength": wavelength,
                 "medium index": medium_index,
                 "sim center": center,
                 "sim radius": radius,
                 "sim index": sphere_index,
                 }

    qpi = qpimage.QPImage(data=field, which_data="field",
                          meta_data=meta_data)
    return qpi
