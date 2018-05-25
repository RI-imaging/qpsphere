import numpy as np
import scipy.special as spspec
import scipy.interpolate as spinterp
from skimage.restoration import unwrap

import qpimage


def interpolate_grid(cin, cout, data, fillval=0):
    """Return the 2D field averaged radially w.r.t. the center"""
    if np.iscomplexobj(data):
        phase = interpolate_grid(
            cin, cout, unwrap.unwrap_phase(np.angle(data)), fillval=0)
        ampli = interpolate_grid(cin, cout, np.abs(data), fillval=1)
        return ampli * np.exp(1j * phase)

    ipol = spinterp.interp2d(x=cin[0], y=cin[1], z=data,
                             kind="linear",
                             copy=False,
                             bounds_error=False,
                             fill_value=fillval)
    return ipol(cout[0], cout[1])


def rytov(radius=5e-6, sphere_index=1.339, medium_index=1.333,
          wavelength=550e-9, pixel_size=1e-7, grid_size=(80, 80),
          center=(39.5, 39.5), radius_sampling=42):
    """Field behind a dielectric sphere in the Rytov approximation

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
    radius_sampling: int
        Number of pixels used to sample the sphere radius when
        computing the Rytov field. The default value of 42
        pixels is a reasonable number for single-cell analysis.

    Returns
    -------
    qpi: qpimage.QPImage
        Quantitative phase data set
    """
    # sample the sphere radius with approximately 42px
    # (rounded to next integer pixel size)
    samp_mult = radius_sampling * pixel_size / radius
    sizex = grid_size[0] * samp_mult
    sizey = grid_size[1] * samp_mult
    grid_size_sim = [np.int(np.round(sizex)),
                     np.int(np.round(sizey))]
    size_factor = grid_size_sim[0] / grid_size[0]
    pixel_size_sim = pixel_size / size_factor

    field = sphere_prop_fslice_bessel(radius=radius,
                                      sphere_index=sphere_index,
                                      medium_index=medium_index,
                                      wavelength=wavelength,
                                      pixel_size=pixel_size_sim,
                                      grid_size=grid_size_sim,
                                      lD=0,
                                      approx="rytov",
                                      zeropad=5,
                                      oversample=1
                                      )

    # interpolate field back to original image coordinates
    # simulation coordinates
    x_sim = (np.arange(grid_size_sim[0]) + .5) * pixel_size_sim
    y_sim = (np.arange(grid_size_sim[1]) + .5) * pixel_size_sim
    # output coordinates
    x = (np.arange(grid_size[0]) + grid_size[0] / 2 - center[0]) * pixel_size
    y = (np.arange(grid_size[1]) + grid_size[1] / 2 - center[1]) * pixel_size

    # Interpolate resulting field with original extent
    field = interpolate_grid(cin=(y_sim, x_sim),
                             cout=(y, x),
                             data=field)

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


def sphere_prop_fslice_bessel(radius, sphere_index, medium_index,
                              wavelength=550e-9, pixel_size=1e-7,
                              grid_size=(80, 80), lD=0, approx="rytov",
                              zeropad=5, oversample=1
                              ):
    """Compute the projection of a disc using the Fourier slice theorem
    and the Bessel function of the first kind of order 1.

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
    lD: float
        The axial distance [m] from the center of the sphere
        at which the field is computed.
    approx: str
        Which approximation to use (either "born" or "rytov")
    zeropad: int
        Zero-padding factor
    oversample: int
        Oversampling factor
    """
    assert approx in ["born", "rytov"]
    assert oversample > 0
    assert zeropad > 0
    assert isinstance(oversample, int)
    assert isinstance(zeropad, int)

    # convert everything to pixels
    radius /= pixel_size
    wavelength /= pixel_size
    lD /= pixel_size

    # apply over-sampling and zero-padding
    wavelength *= oversample
    opad_size = np.array(grid_size) * zeropad * oversample

    assert (int(s) == s for s in opad_size), "grid_size must be integer type"
    opad_size = np.array(np.round(opad_size), dtype=int)
    grid_size = np.array(np.round(grid_size), dtype=int)

    kx = 2 * np.pi * \
        np.fft.ifftshift(np.fft.fftfreq(opad_size[0])).reshape(-1, 1)
    ky = 2 * np.pi * \
        np.fft.ifftshift(np.fft.fftfreq(opad_size[1])).reshape(1, -1)
    km = 2 * np.pi * medium_index / wavelength

    filter_klp = (kx**2 + ky**2 < km**2)

    kz = np.sqrt((km**2 - kx**2 - ky**2) * filter_klp) - km

    r = np.sqrt((kx**2 + ky**2 + kz**2) * filter_klp) / (2 * np.pi)

    comp_id = r != 0
    F = np.zeros_like(r)
    F[comp_id] = spspec.spherical_jn(1, r[comp_id] * radius * np.pi * 2) \
        * radius**2 / r[comp_id] * 2
    # center has analytical value
    center_fft = np.where(np.abs(kx) + np.abs(ky) + np.abs(kz) == 0)
    F[center_fft] = 4 / 3 * np.pi * radius**3

    # object amplitude
    F *= km**2 * ((sphere_index / medium_index)**2 - 1)

    # prefactor A
    M = 1. / km * np.sqrt((km**2 - kx**2 - ky**2) * filter_klp)

    # division factor
    A = -2j * km * M * np.exp(-1j * km * M * lD)

    # rotate phase by half a pixel so the ifft is centered in real space
    if grid_size[0] % 2:
        doffx = 0
    else:
        doffx = .5
    if grid_size[1] % 2:
        doffy = 0
    else:
        doffy = .5
    transl = np.exp(1j * ((doffx) * kx + (doffy) * ky))

    valid = F != 0
    Fconv = np.zeros((opad_size[0], opad_size[1]), dtype=complex)
    Fconv[valid] = F[valid] / A[valid] * transl[valid]

    p = np.fft.ifftn(np.fft.fftshift(Fconv))

    p = np.fft.ifftshift(p)

    if oversample > 1:
        p = p[::oversample, ::oversample]

    if zeropad > 1:
        # Slice
        a0, a1 = np.array(np.floor(opad_size / 2), dtype=int) // oversample
        b0, b1 = np.array(np.floor(grid_size / 2), dtype=int)
        if grid_size[0] % 2 != 0:
            of0 = 1
            a0 += 1
        else:
            of0 = 0
        if grid_size[1] % 2 != 0:
            of1 = 1
            a1 += 1
        else:
            of1 = 0
        # remove zero-padding
        p = p[a0 - b0:a0 + b0 + of0, a1 - b1:a1 + b1 + of1]

    if approx == "born":
        # norm = (u0 + ub)/u0
        # norm = 1 + ub/u0
        return 1 + p / np.exp(1j * km * lD)
    elif approx == "rytov":
        # norm = (u0 + ur)/u0
        # ur = u0 ( exp(ub/u0) -1 )
        # norm = ( u0 + u0 *(exp(ub/u0)-1) )/u0
        # norm = exp(ub/u0)
        return np.exp(p / np.exp(1j * km * lD))
