"""Canny edge detection for QPI analysis of spheres"""
import warnings

import lmfit
import numpy as np
from skimage import feature


class EdgeDetectionError(BaseException):
    pass


class EdgeDetectionWarning(Warning):
    pass


def analyze(qpi, r0, edgekw={}, ret_center=False, ret_edge=False):
    """Determine Refractive index and radius using Canny edge detection

    Compute the refractive index of a spherical phase object by
    detection of an edge in the phase image, a subsequent circle
    fit to the edge, and finally a weighted average over the phase
    image assuming a parabolic phase profile.

    Parameters
    ----------
    qpi: QPImage
        Quantitative phase image information
    r0: float
        Approximate radius of the sphere [m]
    edgekw: dict
        Additional keyword arguments for `contour_canny`
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
    nmed = qpi["medium index"]
    px_m = qpi["pixel size"]
    wl_m = qpi["wavelength"]
    px_wl = px_m / wl_m

    phase = qpi.pha
    # determine edge
    edge = contour_canny(image=phase,
                         radius=r0 / px_m,
                         verbose=False,
                         **edgekw,
                         )
    # fit circle to edge
    center, r = circle_fit(edge)
    # compute average phase density
    avg_phase = average_sphere(phase, center, r)
    # convert phase average to refractive index
    n = nmed + avg_phase / (2 * np.pi * px_wl)
    # convert radius from pixels to meters
    ret = [n, r * px_m]
    if ret_center:
        ret.append(center)
    if ret_edge:
        ret.append(edge)
    return ret


def average_sphere(image, center, radius, weighted=True, ret_crop=False):
    """Compute weighted phase number from a 2D phase image of a sphere

    Parameters
    ----------
    image: 2d ndarray
        Quantitative phase image of a sphere
    center: tuble (x,y)
        Center of the sphere in `image` in ndarray coordinates
    radius: float
        Radius of the sphere in pixels
    weighted: bool
        If `True`, return average phase density weighted with the
        height profile obtained from the radius, otherwise return
        simple average phase density. Weighting gives data points
        at the center of the sphere more weight than those points
        at the boundary of the sphere, avoiding edge artifacts.
    ret_crop: bool
        Return the cropped image.

    Returns
    -------
    average: float
        The average phase value of the sphere from which the refractive
        index can be computed
    cropped_image: 2d ndarray
        Returned if `ret_crop` is True
    """
    sx, sy = image.shape
    x = np.arange(sx).reshape(-1, 1)
    y = np.arange(sy).reshape(1, -1)
    discsq = ((x - center[0])**2 + (y - center[1])**2)
    root = radius**2 - discsq
    # height of the cell for each x and y
    h = 2 * np.sqrt(root * (root > 0))
    # compute phase density
    rho = np.zeros(image.shape)
    hbin = h != 0
    # phase density [rad/px]
    rho[hbin] = image[hbin] / h[hbin]
    if weighted:
        # compute weighted average
        average = np.sum(rho * h) / np.sum(h)
    else:
        # compute simple average
        average = np.sum(rho) / np.sum(hbin)

    ret = average
    if ret_crop:
        ret = (ret, rho)
    return ret


def circle_fit(edge, ret_dev=False):
    """Fit a circle to a boolean edge image

    Parameters
    ----------
    edge: 2d boolean ndarray
        Edge image
    ret_dev: bool
        Return the average deviation of the distance from contour to
        center of the fitted circle.

    Returns
    -------
    center, radius: tuple of floats, float
        Coordinates of the circle. If `ret_dev` is True, then the
        average deviation from the circle is also returned.
    """
    sx, sy = edge.shape
    x = np.linspace(0, sx, sx, endpoint=False).reshape(-1, 1)
    y = np.linspace(0, sy, sy, endpoint=False).reshape(1, -1)
    params = lmfit.Parameters()
    # initial parameters
    sum_edge = np.sum(edge)
    params.add("cx", np.sum(x * edge) / sum_edge)
    params.add("cy", np.sum(y * edge) / sum_edge)
    # data
    xedge, yedge = np.where(edge)
    # minimize
    out = lmfit.minimize(circle_residual, params, args=(xedge, yedge))
    center = (out.params["cx"].value, out.params["cy"].value)
    radii = circle_radii(out.params, xedge, yedge)
    radius = np.mean(radii)

    ret = [center, radius]
    if ret_dev:
        dev = np.average(np.abs(radii - radius))
        ret.append(dev)
    return ret


def circle_radii(params, xedge, yedge):
    cx = params["cx"].value
    cy = params["cy"].value
    radii = np.sqrt((cx - xedge)**2 + (cy - yedge)**2)
    return radii


def circle_residual(params, xedge, yedge):
    radii = circle_radii(params, xedge, yedge)
    return radii - np.mean(radii)


def contour_canny(image, radius, mult_coarse=.40, mult_fine=.1,
                  clip_rmin=.9, clip_rmax=1.1, maxiter=20,
                  verbose=True):
    """Heuristic Canny edge detection for circular objects

    Two Canny-based edge detections with different filter sizes are
    performed to find the outmost contour of an object in a phase image
    while keeping artifacts at a minimum.

    Parameters
    ----------
    image: 2d ndarray
        Image containing an approximately spherically symmetric object
    radius: float
        The approximate object radius in pixels (required for filtering)
    mult_coarse: float
        The coarse edge detection has a filter size of
        ``sigma = mult_coarse * radius``
    mult_fine: float
        The fine edge detection has a filter size of
        ``sigma = mult_fine * radius``
    clip_rmin: float
        Removes edge points that are closer than `clip_rmin` times the
        average radial edge position from the center of the image.
    clip_rmax: float
        Removes edge points that are further than `clip_rmin` times the
        average radial edge position from the center of the image.
    maxiter: int
        Maximum number iterations for coarse edge detection, see Notes
    verbose: bool
        If set to `True`, issues EdgeDetectionWarning where applicable

    Returns
    -------
    edge : 2d boolean ndarray
        The detected edge positions of the object.

    Notes
    -----
    If no edge is found using the filter size defined by `mult_coarse`,
    then the coarse filter size is reduced by a factor of 2 until an
    edge is found or until `maxiter` is reached.

    The edge found using the filter size defined by `mult_fine` is
    heuristically filtered (parts at the center and at the edge of the
    image are removed). This heuristic filtering assumes that the
    circular object is centered in the image.

    See Also
    --------
    skimage.feature.canny: Canny edge detection algorithm used
    """
    image = (image - image.min()) / (image.max() - image.min())

    if radius > image.shape[0] / 2:
        msg = "`radius` in pixels exceeds image size: {}".format(radius)
        raise ValueError(msg)
    # 1. Perform a coarse Canny edge detection. If the edge found is empty,
    # the coarse filter size is reduced by a factor of 2.
    for ii in range(maxiter):
        fact_coarse = .5**ii
        sigma_coarse = radius * mult_coarse * fact_coarse
        edge_coarse = feature.canny(image=image,
                                    sigma=sigma_coarse)
        if np.sum(edge_coarse) != 0:
            break
    else:
        msg = "Could not find edge! Try to reducing `mult_coarse` " \
              + "or increasing `maxiter`."
        raise EdgeDetectionError(msg)

    fact_fine = .7**ii

    if fact_fine != 1 and verbose:
        msg = "The keyword argument `mult_coarse` is too large. " \
              + "If errors occur, adjust `mult_fine` as well.\n" \
              + "Given `mult_coarse`: {}\n".format(mult_coarse) \
              + "New `mult_coarse`: {}\n".format(mult_coarse * fact_coarse) \
              + "Given `mult_fine`: {}\n".format(mult_fine) \
              + "New `mult_fine`: {}".format(mult_fine * fact_fine)
        warnings.warn(msg, EdgeDetectionWarning)

    # 2. Perform a fine Canny edge detection.
    sigma_fine = radius * mult_fine * fact_fine
    edge_fine = feature.canny(image, sigma_fine)

    # 3. Remove parts from the fine edge
    # Assume that the object is centered.
    sx, sy = image.shape
    x = np.linspace(-sx / 2, sx / 2, sx, endpoint=True).reshape(-1, 1)
    y = np.linspace(-sy / 2, sy / 2, sy, endpoint=True).reshape(1, -1)
    # 3.a. Remove detected edge parts from the corners of the image
    # Radius of this disk is approximately
    ellipse = (x / sx)**2 + (y / sy)**2 < .25
    edge_fine *= ellipse
    edge_coarse *= ellipse

    if np.sum(edge_fine):
        # 3.b Also filter inside of edge
        rad = np.sqrt(x**2 + y**2)
        # Filter coarse edge with `clip_rmin` and `clip_rmax`
        rad_coarse = rad * edge_coarse
        avg_coarse = np.sum(rad_coarse) / np.sum(edge_coarse)
        rad_coarse[rad_coarse < avg_coarse * clip_rmin] = 0
        rad_coarse[rad_coarse > avg_coarse * clip_rmax] = 0
        # Filter inside of fine edge with smallest radius of
        # coarse edge, i.e. `rad_coarse.min()`.
        rad_fine = rad * edge_fine
        if np.sum(rad_coarse):
            edge_fine[rad_fine < rad_coarse[rad_coarse != 0].min()] = 0
        # Filter outside of fine edge with `clip_rmax` twice
        for __ in range(2):
            rad_fine = rad * edge_fine
            avg_fine = np.sum(rad_fine) / np.sum(edge_fine)
            edge_fine[rad_fine > avg_fine * clip_rmax] = 0
    elif np.sum(edge_coarse):
        # No fine edge detected.
        edge_fine = edge_coarse
    else:
        msg = "Could not find edge! Try reducing `mult_coarse` " \
              + "and `mult_fine`."
        raise EdgeDetectionError(msg)
    # make sure there are more than 4 points
    if np.sum(edge_fine) < 4:
        msg = "Detected edge too small! Try increasing `maxiter`, " \
              + "modifying `radius`, or reducing `mult_coarse`."
        raise EdgeDetectionError(msg)
    return edge_fine
