import nrefocus
import numpy as np
import scipy.interpolate as spinterp
from skimage.restoration import unwrap

import qpimage

from ._bhfield import simulate_sphere


def mie_avg(radius=5e-6, sphere_index=1.339, medium_index=1.333,
            wavelength=550e-9, pixel_size=1e-7, grid_size=(80, 80),
            center=(39.5, 39.5), interpolate=3, arp=True):
    """Mie-simulated non-polarized field behind a dielectric sphere

    Parameters
    ----------
    radius: float
        Radius of the sphere [m]
    sphere_index: float
        Refractive index of the sphere
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
    interpolate: int
        Compute the radial field with sampling that is by a factor of
        `interpolate` higher than the required data and interpolate the
        2D field from there.
    arp: bool
        Use arbitrary precision (ARPREC) in BHFIELD computations

    Returns
    -------
    qpi: qpimage.QPImage
        Quantitative phase data set
    """
    center = np.array(center)
    grid_size = np.array(grid_size)
    # simulation parameters
    radius_um = radius * 1e6  # radius of sphere in um
    propd_um = radius_um  # simulate propagation through full sphere
    propd_lamd = radius / wavelength  # radius in wavelengths
    wave_nm = wavelength * 1e9

    kwargs = {"radius_sphere_um": radius_um,
              "refractive_index_medium": medium_index,
              "refractive_index_sphere": sphere_index,
              "measurement_position_um": propd_um,
              "wavelength_nm": wave_nm}

    upres = wavelength / pixel_size * interpolate
    max_off = np.max(np.abs(grid_size / 2 - .5 - center))

    latsize = int(np.round((np.max(grid_size) + max_off)))

    num = latsize * upres / 2
    # find the maximum interpolation range in the 2d image

    bignum = int(np.ceil(np.sqrt(np.sum((np.array(grid_size) /
                                         2 + max_off)**2))) * interpolate)

    # Compare this number to the radius of the sphere and cut it off at
    # three times the radius.
    radnum = int(np.ceil(3 * radius / pixel_size) * interpolate)
    bignum = min(bignum, radnum)

    latsize *= bignum / num
    latsize *= wavelength * 1e6
    upres /= wavelength * 1e6

    background = np.exp(1j * 2 * np.pi * propd_lamd * medium_index)

    # [sic]: Not times upres
    ofx_px = grid_size[0] / 2 - center[0]
    ofy_px = grid_size[1] / 2 - center[1]

    kwargsx = kwargs.copy()
    kwargsx.update({"size_simulation_um": (latsize / 2, 1 / upres),
                    "shape_grid": (bignum, 1),
                    "offset_x_um": -latsize / 4,
                    "offset_y_um": 0})

    fieldx = simulate_sphere(arp=arp, **kwargsx) / background

    kwargsy = kwargs.copy()
    kwargsy.update({"size_simulation_um": (1 / upres, latsize / 2),
                    "shape_grid": (1, bignum),
                    "offset_x_um": 0,
                    "offset_y_um": -latsize / 4})
    fieldy = simulate_sphere(arp=arp, **kwargsy) / background

    field = (fieldx.flatten() + fieldy.flatten()) / 2

    xo = np.linspace(0, bignum, bignum, endpoint=True) / interpolate

    x = np.linspace(-grid_size[0] / 2,
                    grid_size[0] / 2,
                    grid_size[0] * interpolate,
                    endpoint=True)

    y = np.linspace(-grid_size[1] / 2,
                    grid_size[1] / 2,
                    grid_size[1] * interpolate,
                    endpoint=True)

    yv, xv = np.meshgrid(y, x)
    r = np.sqrt(xv**2 + yv**2)
    inpt_kwargs = {"kind": "linear",
                   "assume_sorted": True,
                   "bounds_error": False,
                   }

    ipltph = spinterp.interp1d(xo, np.unwrap(
        np.angle(field)), fill_value=0, **inpt_kwargs)
    ipltam = spinterp.interp1d(xo, np.abs(field), fill_value=1, **inpt_kwargs)
    phase2d = ipltph(r)
    field2d = ipltam(r) * np.exp(1j * phase2d)

    # Numerical refocusing
    # We need to perform numerical focusing with the upsampled array,
    # or else we will loose spatial information and the resulting
    # spherical image becomes asymmetric.
    refoc_field2d = nrefocus.refocus(field2d,
                                     d=-(radius / pixel_size) * interpolate,
                                     nm=medium_index,
                                     res=wavelength / pixel_size * interpolate)

    # Perform new interpolation on requested grid
    # We might introduce an offset here:
    phase = unwrap.unwrap_phase(np.angle(refoc_field2d), seed=47)

    # detect and remove multiple-2PI phase offset
    pha_offset = np.median(phase[:3])
    num_2pi = np.round(pha_offset / (2 * np.pi))
    if num_2pi:
        phase -= num_2pi * 2 * np.pi

    ampli = np.abs(refoc_field2d)
    intpp = spinterp.RectBivariateSpline(x, y, phase, kx=1, ky=1)
    intpa = spinterp.RectBivariateSpline(x, y, ampli, kx=1, ky=1)

    xp = np.linspace(-grid_size[0] / 2,
                     grid_size[0] / 2,
                     grid_size[0],
                     endpoint=False) + ofx_px

    yp = np.linspace(-grid_size[1] / 2,
                     grid_size[1] / 2,
                     grid_size[1],
                     endpoint=False) + ofy_px

    amp_off = intpa(xp, yp)
    pha_off = intpp(xp, yp)

    meta_data = {"pixel size": pixel_size,
                 "wavelength": wavelength,
                 "medium index": medium_index,
                 "sim center": center,
                 "sim radius": radius,
                 "sim index": sphere_index,
                 }

    qpi = qpimage.QPImage(data=(pha_off, amp_off),
                          which_data="phase,amplitude",
                          meta_data=meta_data)

    return qpi
