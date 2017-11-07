from ._version import version as __version__  # noqa: F401
from . import edgefit  # noqa: F401
from .models import simulate  # noqa: F401


def analyze(qpi, n0=None, r0=None, method="edge", model="projection",
            ret_center=False, edgekw={}, imagekw={}):
    """Determine refractive index and radius of a spherical object

    Parameters
    ----------
    qpi: QPImage
        Quantitative phase image information
    n0: float
        Approximate refractive index of the phase object,
        estimated with the edge-detection approach if not given
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

    ret_center: bool
        Return the center coordinate of the sphere

    Returns
    -------
    n: float
        Computed refractive index
    r: float
        Computed radius [m]
    center: tuple of floats
        Center position of the sphere [px], only returned
        if `ret_center` is `True`
    """
    if method == "edge":
        if model != "projection":
            raise ValueError("`method='edge'` requires `model='projection'`!")
        if r0 is None:
            raise ValueError("`method='edge'` requires estimate of `r0`!")
        return edgefit.analyze(qpi=qpi,
                               r0=r0,
                               edgekw=edgekw,
                               ret_center=ret_center,
                               ret_edge=False,
                               )
    else:
        raise NotImplementedError("2D phase image fit not yet available!")
