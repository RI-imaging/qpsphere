import numpy as np

from . import mod_rytov


#: correction parameters (see :func:`correct_rytov_output`)
RSC_PARAMS = {42: {"na": 1.936,
                   "nb": -0.012,
                   "ra": -2.431,
                   "rb": -.753,
                   "rc": 1.001}
              }


def correct_rytov_sc_input(radius_sc, sphere_index_sc, medium_index,
                           radius_sampling):
    """Inverse correction of refractive index and radius for Rytov

    This method returns the inverse of :func:`correct_rytov_output`.

    Parameters
    ----------
    radius_sc: float
        Systematically corrected radius of the sphere [m]
    sphere_index_sc: float
        Systematically corrected refractive index of the sphere
    medium_index: float
        Refractive index of the surrounding medium
    radius_sampling: int
        Number of pixels used to sample the sphere radius when
        computing the Rytov field.

    Returns
    -------
    radius: float
        Fitted radius of the sphere [m]
    sphere_index: float
        Fitted refractive index of the sphere

    See Also
    --------
    correct_rytov_output: the inverse of this method
    """
    params = get_params(radius_sampling)

    # sage script:
    # var('sphere_index, sphere_index_sc, na, nb, medium_index')
    # x = sphere_index / medium_index - 1
    # eq = sphere_index_sc == sphere_index + ( na*x^2 + nb*x) * medium_index
    # solve([eq], [sphere_index])
    # (take the positive sign solution)
    na = params["na"]
    nb = params["nb"]

    prefac = medium_index / (2 * na)
    sm = 2 * na - nb - 1
    rt = nb**2 - 4 * na + 2 * nb + 1 + 4 / medium_index * na * sphere_index_sc
    sphere_index = prefac * (sm + np.sqrt(rt))

    x = sphere_index / medium_index - 1

    radius = radius_sc / (params["ra"] * x**2
                          + params["rb"] * x
                          + params["rc"])

    return radius, sphere_index


def correct_rytov_output(radius, sphere_index, medium_index, radius_sampling):
    """Error-correction of refractive index and radius for Rytov

    This method corrects the fitting results for `radius`
    :math:`r_\text{Ryt}` and `sphere_index` :math:`n_\text{Ryt}`
    obtained using :func:`qpsphere.models.mod_rytov.rytov` using
    the approach described in :cite:`Mueller2018` (eqns. 3,4, and 5).

    .. math::

        n_\text{Ryt-SC} &= n_\text{Ryt} + n_\text{med} \cdot
                           \left( a_n x^2 + b_n x + c_n \right)
        r_\text{Ryt-SC} &= r_\text{Ryt} \cdot
                           \left( a_r x^2 +b_r x + c_r \right)
        &\text{with~} x = \frac{n_\text{Ryt}}{n_\text{med}} - 1

    Parameters
    ----------
    radius: float
        Fitted radius of the sphere :math:`r_\text{Ryt}` [m]
    sphere_index: float
        Fitted refractive index of the sphere :math:`n_\text{Ryt}`
    medium_index: float
        Refractive index of the surrounding medium :math:`n_\text{med}`
    radius_sampling: int
        Number of pixels used to sample the sphere radius when
        computing the Rytov field.

    Returns
    -------
    radius_sc: float
        Systematically corrected radius of the sphere
        :math:`r_\text{Ryt-SC}` [m]
    sphere_index_sc: float
        Systematically corrected refractive index of the sphere
        :math:`n_\text{Ryt-SC}`

    See Also
    --------
    correct_rytov_sc_input: the inverse of this method
    """
    params = get_params(radius_sampling)

    x = sphere_index / medium_index - 1

    radius_sc = radius * (params["ra"] * x**2
                          + params["rb"] * x
                          + params["rc"])

    sphere_index_sc = sphere_index + medium_index * (params["na"] * x**2
                                                     + params["nb"] * x)

    return radius_sc, sphere_index_sc


def get_params(radius_sampling):
    if radius_sampling not in RSC_PARAMS:
        msg = "`radius_sampling={}` not available. ".format(radius_sampling) \
              + "Please use one of: {}".format(RSC_PARAMS.keys())
        raise ValueError(msg)
    return RSC_PARAMS[radius_sampling]


def rytov_sc(radius=5e-6, sphere_index=1.339, medium_index=1.333,
             wavelength=550e-9, pixel_size=1e-7, grid_size=(80, 80),
             center=(39.5, 39.5), radius_sampling=42):
    """Field behind a dielectric sphere, systematically corrected Rytov

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

    Notes
    -----

    """
    r_ryt, n_ryt = correct_rytov_sc_input(radius_sc=radius,
                                          sphere_index_sc=sphere_index,
                                          medium_index=medium_index,
                                          radius_sampling=radius_sampling)

    qpi = mod_rytov.rytov(radius=r_ryt,
                          sphere_index=n_ryt,
                          medium_index=medium_index,
                          wavelength=wavelength,
                          pixel_size=pixel_size,
                          grid_size=grid_size,
                          center=center,
                          radius_sampling=radius_sampling)

    # update correct simulation parameters
    qpi["sim radius"] = radius
    qpi["sim index"] = sphere_index

    return qpi
