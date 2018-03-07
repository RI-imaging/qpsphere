from ._version import version as __version__  # noqa: F401
from . import edgefit
from . import imagefit
from . import models  # noqa: F401
from .models import simulate  # noqa: F401
from . import util  # noqa: F401


def analyze(qpi, r0, method="edge", model="projection", edgekw={}, imagekw={},
            ret_center=False, ret_pha_offset=False, ret_qpi=False):
    """Determine refractive index and radius of a spherical object

    Parameters
    ----------
    qpi: QPImage
        Quantitative phase image data
    r0: float
        Approximate radius of the sphere [m]
    method: str
        The method used to determine the refractive index
        can either be "edge" (determine the radius from the
        edge detected in the phase image) or "image" (perform
        a 2D phase image fit).
    model: str
        The light-scattering model used by `method`. If
        `method` is "edge", only "projection" is allowed.
        If `method` is "image", `model` can be one of
        "mie", "projection", "rytov", or "rytov-sc".
    edgekw: dict
        Keyword arguments for tuning the edge detection algorithm,
        see :func:`qpsphere.edgefit.contour_canny`.
    imagekw: dict
        Keyword arguments for tuning the image fitting algorithm,
        see :func:`qpsphere.imagefit.alg.match_phase`
    ret_center: bool
        If True, return the center coordinate of the sphere.
    ret_pha_offset: bool
        If True, return the phase image background offset.
    ret_qpi: bool
        If True, return the modeled data as a :class:`qpimage.QPImage`.

    Returns
    -------
    n: float
        Computed refractive index
    r: float
        Computed radius [m]
    c: tuple of floats
        Only returned if `ret_center` is True
        Center position of the sphere [px]
    pha_offset: float
        Only returned if `ret_pha_offset` is True
        Phase image background offset
    qpi_sim: qpimage.QPImage
        Only returned if `ret_qpi` is True
        Modeled data

    Notes
    -----
    If `method` is "image", then the "edge" method is used
    as a first step to estimate initial parameters for radius,
    refractive index, and position of the sphere using `edgekw`.
    If this behavior is not desired, please make use of the
    method :func:`qpsphere.imagefit.analyze`.
    """
    if method == "edge":
        if model != "projection":
            raise ValueError("`method='edge'` requires `model='projection'`!")
        n, r, c = edgefit.analyze(qpi=qpi,
                                  r0=r0,
                                  edgekw=edgekw,
                                  ret_center=True,
                                  ret_edge=False,
                                  )
        res = [n, r]
        if ret_center:
            res.append(c)
        if ret_pha_offset:
            res.append(0)
        if ret_qpi:
            qpi_sim = simulate(radius=r,
                               sphere_index=n,
                               medium_index=qpi["medium index"],
                               wavelength=qpi["wavelength"],
                               grid_size=qpi.shape,
                               model="projection",
                               pixel_size=qpi["pixel size"],
                               center=c)
            res.append(qpi_sim)
    elif method == "image":
        n0, r0, c0 = edgefit.analyze(qpi=qpi,
                                     r0=r0,
                                     edgekw=edgekw,
                                     ret_center=True,
                                     ret_edge=False,
                                     )
        res = imagefit.analyze(qpi=qpi,
                               model=model,
                               n0=n0,
                               r0=r0,
                               c0=c0,
                               imagekw=imagekw,
                               ret_center=ret_center,
                               ret_pha_offset=ret_pha_offset,
                               ret_qpi=ret_qpi
                               )
    else:
        raise NotImplementedError("`method` must be 'edge' or 'image'!")

    return res
