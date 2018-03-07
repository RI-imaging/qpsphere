from .alg import match_phase


def analyze(qpi, model, n0, r0, c0=None, imagekw={},
            ret_center=False, ret_pha_offset=False, ret_qpi=False):
    """Fit refractive index and radius to a phase image of a sphere

    Parameters
    ----------
    qpi: QPImage
        Quantitative phase image information
    model: str
        Name of the light-scattering model
        (see :const:`qpsphere.models.available`)
    n0: float
        Approximate refractive index of the sphere
    r0: float
        Approximate radius of the sphere [m]
    c0: tuple of (float, float)
        Approximate center position in ndarray index coordinates [px];
        if set to `None` (default), the center of the image is used.
    imagekw: dict
        Additional keyword arguments to
        :func:`qpsphere.imagefit.alg.match_phase`.
    ret_center: bool
        Return the center coordinate of the sphere
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
    """
    res = match_phase(qpi, model=model, n0=n0, r0=r0, c0=c0,
                      ret_center=ret_center,
                      ret_pha_offset=ret_pha_offset,
                      ret_qpi=ret_qpi,
                      **imagekw)
    return res
