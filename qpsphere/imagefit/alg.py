import time
import warnings

import h5py
import numpy as np

import qpimage

from .interp import SpherePhaseInterpolator


def match_phase(qpi, model, n0, r0, c0=None, pha_offset=0,
                fix_pha_offset=False, nrel=.10, rrel=.05, crel=.05,
                stop_dn=.0005, stop_dr=.0010, stop_dc=1, min_iter=3,
                max_iter=100, ret_center=False, ret_pha_offset=False,
                ret_qpi=False, ret_num_iter=False, ret_interim=False,
                verbose=0, verbose_h5path="./match_phase_error.h5"):
    """Fit a scattering model to a quantitative phase image

    Parameters
    ----------
    qpi: qpimage.QPImage
        QPI data to fit (e.g. experimental data)
    model: str
        Name of the light-scattering model
        (see :const:`qpsphere.models.available`)
    n0: float
        Initial refractive index of the sphere
    r0: float
        Initial radius of the sphere [m]
    c0: tuple of (float, float)
        Initial center position of the sphere in ndarray index
        coordinates [px]; if set to `None` (default), the center
        of the image is used.
    pha_offset: float
        Initial phase offset [rad]
    fix_pha_offset: bool
        If True, do not fit the phase offset `pha_offset`. The phase
        offset is determined from the mean of all pixels whose absolute
        phase is

        - below 1% of the modeled phase and
        - within a 5px or 20% border (depending on which is larger)
          around the phase image.
    nrel: float
        Determines the border of the interpolation range for the
        refractive index: [n-(n-nmed)*nrel, n+(n-nmed)*nrel]
        with nmed=qpi["medium_index"] and, initially, n=n0.
    rrel: float
        Determines the border of the interpolation range for the
        radius: [r*(1-rrel), r*(1+rrel)] with, initially, r=r0.
    crel: float
        Determines the border of the interpolation range for the
        center position: [cxy - dc, cxy + dc] with the center
        position (along x or y) cxy, and the interval radius dc
        defined by dc=max(lambda, crel * r0) with the vacuum
        wavelength lambda=qpi["wavelenght"].
    stop_dn: float
        Stopping criterion for refractive index
    stop_dr: float
        Stopping criterion for radius
    stop_dc: float
        Stopping criterion for lateral offsets
    min_iter: int
        Minimum number of fitting iterations to perform
    max_iter: int
        Maximum number of fitting iterations to perform
    ret_center: bool
        If True, return the fitted center coordinates
    ret_pha_offset: bool
        If True, return the fitted phase offset
    ret_qpi: bool
        If True, return the final fit as a data set
    ret_num_iter: bool
        If True, return the number of iterations
    ret_interim: bool
        If True, return intermediate parameters of each iteration
    verbose: int
        Higher values increase verbosity
    verbose_h5path: str
        Path to hdf5 output file, created when `verbosity >= 2`

    Returns
    -------
    n: float
        Fitted refractive index
    r: float
        Fitted radius [m]
    c: tuple of (float, float)
        Only returned if `ret_center` is True
        Center position of the sphere in ndarray index coordinates [px]
    pha_offset: float
        Only returned if `ret_pha_offset` is True
        Fitted phase offset [rad]
    qpi: qpimage.QPImage
        Only returned if `ret_qpi` is True
        Simulation using `model` with the final fit parameters
    num_iter: int
        Only returned if `ret_num_iter` is True
        Number of iterations performed; negative number is
        returned when iteration fails
    interim: list
        Only returned if `ret_interim` is True
        Intermediate fitting parameters
    """
    if not isinstance(qpi, qpimage.QPImage):
        raise ValueError("`qpi` must be instance of `QPImage`!")
    for var in ["medium index", "pixel size", "wavelength"]:
        if var not in qpi:
            raise ValueError("meta data '{}' not defined in `qpi`!")

    if c0 is None:
        c0 = [qpi.shape[0] / 2, qpi.shape[1] / 2]

    model_kwargs = {"radius": r0,
                    "sphere_index": n0,
                    "medium_index": qpi["medium index"],
                    "wavelength": qpi["wavelength"],
                    "pixel_size": qpi["pixel size"],
                    "grid_size": qpi.shape,
                    "center": c0
                    }

    spi = SpherePhaseInterpolator(model=model,
                                  model_kwargs=model_kwargs,
                                  pha_offset=pha_offset,
                                  nrel=nrel,
                                  rrel=rrel,
                                  verbose=verbose)

    # Results recorder to detect stuck iterations
    recorder = []

    # intermediate results
    interim = []
    interim.append([0, spi.params])

    phase = qpi.pha
    range_ipol = 47
    range_off = 13
    # allow to vary center offset for 5 % of radius or 1 wavelengths
    dc = max(qpi["wavelength"], crel * r0) / qpi["pixel size"]  # [px]
    if verbose:
        print("Starting phase fitting.")
    ii = 0
    message = None
    if "identifier" in qpi:
        ident = qpi["identifier"]
    else:
        ident = str(time.time())
    while True:
        if verbose >= 2:
            export_phase_error_hdf5(h5path=verbose_h5path,
                                    identifier=ident,
                                    index=ii,
                                    phase=phase,
                                    mphase=spi.get_phase(),
                                    model=model,
                                    n0=n0,
                                    r0=r0,
                                    spi_params=spi.params)

        ii += 1

        # remember old values
        r_old = spi.radius
        n_old = spi.sphere_index

        # 1st step: vary radius
        rs = np.linspace(
            spi.range_r[0], spi.range_r[1], range_ipol, endpoint=True)
        assert np.allclose(np.min(np.abs(rs - spi.radius)), 0)
        lsqs = []
        for ri in rs:
            phasei = spi.get_phase(rintp=ri)
            lsqs.append(sq_phase_diff(phase, phasei))
        idr = np.argmin(lsqs)
        spi.radius = rs[idr]

        # 2nd step: vary n_object
        ns = np.linspace(
            spi.range_n[0], spi.range_n[1], range_ipol, endpoint=True)
        assert np.allclose(np.min(np.abs(ns - spi.sphere_index)), 0)
        lsqs = []
        for ni in ns:
            phasei = spi.get_phase(nintp=ni)
            lsqs.append(sq_phase_diff(phase, phasei))
        idn = np.argmin(lsqs)
        spi.sphere_index = ns[idn]

        # 3rd step: vary center position
        x = np.linspace(-dc, dc, range_off, endpoint=True)
        assert np.allclose(np.min(np.abs(x)), 0)
        xintp, yintp = np.meshgrid(x, x)
        lsqs = []
        for xoff, yoff in zip(xintp.flatten(), yintp.flatten()):
            phasei = spi.get_phase(delta_offset_x=xoff, delta_offset_y=yoff)
            err = sq_phase_diff(phase, phasei)
            lsqs.append(err)

        idc = np.argmin(lsqs)
        deltax = xintp.flatten()[idc]
        deltay = yintp.flatten()[idc]

        # offsets must be added incrementally, because they are not overridden
        # in the 3rd step
        spi.posx_offset = spi.posx_offset - deltax
        spi.posy_offset = spi.posy_offset - deltay

        if not fix_pha_offset:
            # Use average phase at image border without sphere
            cabphase = spi.get_phase() - spi.pha_offset
            # Determine background
            cabphase[np.abs(cabphase) > .01 * np.abs(cabphase).max()] = np.nan
            cb_border = max(5, min(cabphase.shape) // 5)
            cabphase[cb_border:-cb_border, cb_border:-cb_border] = np.nan
            phai_offset = np.nanmean(cabphase - phase)

            if np.isnan(phai_offset):
                phai_offset = 0

            spi.pha_offset = - phai_offset

        if verbose == 1:
            print("Iteration {}: n={:.5e}, r={:.5e}m".format(ii,
                                                             spi.sphere_index,
                                                             spi.radius))
        elif verbose >= 2:
            print("Iteration {}: {}".format(ii, spi.params))

        interim.append([ii, spi.params])

        # update accuracies
        if (idn > range_ipol / 2 - range_ipol / 10 and
                idn < range_ipol / 2 + range_ipol / 10):
            spi.dn /= 2
            if verbose >= 2:
                print("Halved search interval: spi.dn={:.8f}".format(spi.dn))
        if (idr > range_ipol / 2 - range_ipol / 10 and
                idr < range_ipol / 2 + range_ipol / 10):
            spi.dr /= 2
            if verbose >= 2:
                print("Halved search interval: spi.dr={:.8f}".format(spi.dr))
        if deltax**2 + deltay**2 < dc**2:
            dc /= 2
            if verbose >= 2:
                print("Halved search interval: dc={:.8f}".format(dc))

        if ii < min_iter:
            if verbose:
                print("Keep iterating because `min_iter`={}.".format(min_iter))
            continue
        elif ii >= max_iter:
            ii *= -1
            if verbose:
                print("Stopping iteration: reached `max_iter`={}".format(
                    max_iter))
            message = "fail, reached maximum number of iterations"
            break

        if stop_dc:
            # check movement of center location and enforce next iteration
            curoff = np.sqrt(deltax**2 + deltay**2)
            if curoff > stop_dc:
                if verbose:
                    print("Keep iterating because center location moved by "
                          + "{} > `stop_dc`={}.".format(curoff, stop_dc))
                continue

        if (abs(spi.radius - r_old) / spi.radius < stop_dr and
                abs(spi.sphere_index - n_old) < stop_dn):
            # Radius, refractive index, and center position changed below
            # user-defined threshold.
            if verbose:
                print("Stopping iteration: `stop_dr` and `stop_dn` satisfied")
            message = "success, satisfied stopping criteria"
            break

        thisresult = (spi.sphere_index, spi.radius)
        recorder.append(thisresult)
        if recorder.count(thisresult) > 2:
            ii *= -1
            # We have already had this result 2 times and therefore we abort.
            # TODO:
            # - Select the one with the least error
            warnings.warn("Aborting stuck iteration for {}!".format(qpi))
            if verbose:
                print("Stop iteration: encountered same parameters twice.")
            message = "fail, same parameters encountered twice"
            break

        if verbose >= 2:
            infostring = ""
            if not abs(spi.sphere_index - n_old) < stop_dn:
                infostring += " delta_n = {} > {}".format(
                    abs(spi.sphere_index - n_old), stop_dn)
            if not abs(spi.radius - r_old) / spi.radius < stop_dr:
                infostring += " delta_r = {} > {}".format(
                    abs(spi.radius - r_old) / spi.radius, stop_dr)
            print("Keep iterating: {} (no convergence)".format(infostring))

    if verbose:
        print("Number of iterations: {}".format(ii))
        print("Stopping rationale: {}".format(message))

    if verbose >= 2:
        export_phase_error_hdf5(h5path=verbose_h5path,
                                identifier=ident,
                                index=ii,
                                phase=phase,
                                mphase=spi.get_phase(),
                                model=model,
                                n0=n0,
                                r0=r0,
                                spi_params=spi.params)

    res = [spi.sphere_index, spi.radius]

    if ret_center:
        res += [[spi.posx_offset, spi.posy_offset]]
    if ret_pha_offset:
        res += [spi.pha_offset]
    if ret_qpi:
        res += [spi.compute_qpi()]
    if ret_num_iter:
        res += [ii]
    if ret_interim:
        res += [interim]

    return res


def sq_phase_diff(pha_a, pha_b):
    """Compute sum of squares error between two arrays

    Parameters
    ----------
    pha_a, pha_b: 2d real-valued np.ndarrays
        Phase data to compare

    Returns
    -------
    sumsq: float
        Sum of squares of differences
    """
    err = np.sum((pha_a - pha_b)**2)
    return err


def export_phase_error_hdf5(h5path, identifier, index, phase, mphase,
                            model, n0, r0, spi_params):
    """Export the phase error to an hdf5 file

    Parameters
    ----------
    h5path: str or pathlib.Path
        path to hdf5 output file
    identifier: str
        unique identifier of the input phase
        (e.g. `qpimage.QPImage["identifier"]`)
    index: int
        iteration index
    phase: 2d real-valued np.ndarray
        phase image
    mphase: 2d real-valued np.ndarray
        reference phase image
    model: str
        sphere model name
    n0: float
        initial object index
    r0: float
        initial object radius [m]
    spi_params: dict
        parameter dictionary of :func:`SpherePhaseInterpolator`
    """
    with h5py.File(h5path, mode="a") as h5:
        if identifier in h5:
            grp = h5[identifier]
        else:
            grp = h5.create_group(identifier)
        ds = grp.create_dataset("phase_error_{:05d}".format(index),
                                data=mphase-phase)
        ds.attrs["index initial"] = n0
        ds.attrs["radius initial"] = r0
        ds.attrs["sim model"] = model
        ds.attrs["sim index"] = spi_params["sphere_index"]
        ds.attrs["sim radius"] = spi_params["radius"]
        ds.attrs["sim center"] = spi_params["center"]
        ds.attrs["fit iteration"] = index
        ds.attrs["fit iteration"] = index
