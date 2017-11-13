from .projection import projection


available = {"projection": projection,
             }


def simulate(radius=5, sphere_index=1.339, medium_index=1.333,
             wavelength=550e-9, pixel_size=1e-7, model="projection",
             grid_size=(80, 80), center=(40, 40)):
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
    pixel_size: float
        Pixel size [m]
    model: str
        Sphere model to use (see `available`)
    grid_size: tuple of floats
        Resulting image size in x and y [px]
    center: tuple of floats
        Center position in image coordinates [px]

    Returns
    -------
    qpi: qpimage.QPImage
        Quantitative phase data set
    """
    model = available[model]
    qpi = model(radius=radius,
                sphere_index=sphere_index,
                medium_index=medium_index,
                wavelength=wavelength,
                pixel_size=pixel_size,
                grid_size=grid_size,
                center=center)
    return qpi
