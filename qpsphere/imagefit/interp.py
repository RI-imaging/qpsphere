import numpy as np
import scipy.interpolate as spintp
import time

from .. import models


class SpherePhaseInterpolator(object):
    def __init__(self, model, model_kwargs,
                 pha_offset=0, nrel=0.1, rrel=0.05, verbose=0):
        """Interpolation in-between modeled phase images

        Parameters
        ----------
        model: str
            Name of the light-scattering model
            (see :const:`qpsphere.models.available`)
        model_kwargs: dict
            Keyword arguments for the sphere model; must contain:

            - radius: float
                 Radius of the sphere [m]
            - sphere_index: float
                 Refractive index of the object
            - medium_index: float
                 Refractive index of the surrounding medium
            - wavelength: float
                 Vacuum wavelength of the imaging light [m]
            - pixel_size: float
                 Pixel size [m]
            - grid_size: tuple of floats
                 Resulting image size in x and y [px]
            - center: tuple of floats
                 Center position in image coordinates [px]
        pha_offset: float
            Phase offset added to the interpolation result
        nrel : float
            Determines the border of the interpolation range for the
            refractive index: [n-(n-nmed)*nrel, n+(n-nmed)*nrel]
            with n=model_kwargs["sphere_index"] and
            nmed=model_kwargs["medium_index"]
        rrel : float
            Determines the border of the interpolation range for the
            radius: [r*(1-rrel), r*(1+rrel)] with
            r=model_kwargs["radius"]
        verbose: int
            Increases verbosity.
        """
        self.verbose = verbose

        #: scattering model
        self.model = model
        #: scattering model function
        self.sphere_method = models.model_dict[model]
        #: scattering model keyword arguments
        self.model_kwargs = model_kwargs
        #: current sphere radius [m]
        self.radius = model_kwargs["radius"]
        #: current sphere index
        self.sphere_index = model_kwargs["sphere_index"]
        #: current background phase offset
        self.pha_offset = pha_offset
        #: current pixel offset in x
        self.posx_offset = model_kwargs["center"][0]
        #: current pixel offset in y
        self.posy_offset = model_kwargs["center"][1]
        #: half of current search interval size for refractive index
        self.dn = abs(
            (self.sphere_index - model_kwargs["medium_index"]) * nrel)
        #: half of current search interval size for radius [m]
        self.dr = self.radius * rrel

        # dictionary for determining if a new phase image
        # needs to be computed
        self._n_border = np.zeros((3, 3), dtype=float)
        self._r_border = np.zeros((3, 3), dtype=float)

        # border phase images
        self._border_pha = {}

    @property
    def params(self):
        """Current interpolation parameter dictionary"""
        par = {"radius": self.radius,
               "sphere_index": self.sphere_index,
               "pha_offset": self.pha_offset,
               "center": [self.posx_offset, self.posy_offset]
               }
        return par

    @property
    def range_n(self):
        """Current interpolation range of refractive index"""
        return self.sphere_index - self.dn, self.sphere_index + self.dn

    @property
    def range_r(self):
        """Current interpolation range of radius"""
        return self.radius - self.dr, self.radius + self.dr

    def compute_qpi(self):
        """Compute model data with current parameters

        Returns
        -------
        qpi: qpimage.QPImage
            Modeled phase data

        Notes
        -----
        The model image might deviate from the fitted image
        because of interpolation during the fitting process.
        """
        kwargs = self.model_kwargs.copy()
        kwargs["radius"] = self.radius
        kwargs["sphere_index"] = self.sphere_index
        kwargs["center"] = [self.posx_offset, self.posy_offset]
        qpi = self.sphere_method(**kwargs)
        # apply phase offset
        bg_data = np.ones(qpi.shape) * -self.pha_offset
        qpi.set_bg_data(bg_data=bg_data, which_data="phase")
        return qpi

    def get_border_phase(self, idn=0, idr=0):
        """Return one of nine border fields

        Parameters
        ----------
        idn: int
            Index for refractive index.
            One of -1 (left), 0 (center), 1 (right)
        idr: int
            Index for radius.
            One of -1 (left), 0 (center), 1 (right)
        """
        assert idn in [-1, 0, 1]
        assert idr in [-1, 0, 1]

        n = self.sphere_index + self.dn * idn
        r = self.radius + self.dr * idr

        # convert to array indices
        idn += 1
        idr += 1
        # find out whether we need to compute a new border field
        if self._n_border[idn, idr] == n and self._r_border[idn, idr] == r:
            if self.verbose > 3:
                print("Using cached border phase (n{}, r{})".format(idn, idr))
            # return previously computed field
            pha = self._border_pha[(idn, idr)]
        else:
            if self.verbose > 3:
                print("Computing border phase (n{}, r{})".format(idn, idr))
            kwargs = self.model_kwargs.copy()
            kwargs["radius"] = r
            kwargs["sphere_index"] = n
            kwargs["center"] = [self.posx_offset, self.posy_offset]
            tb = time.time()
            pha = self.sphere_method(**kwargs).pha
            if self.verbose > 2:
                print("Border phase computation time:",
                      self.sphere_method.__module__, time.time() - tb)
            self._border_pha[(idn, idr)] = pha
            self._n_border[idn, idr] = n
            self._r_border[idn, idr] = r

        return pha

    def get_phase(self, nintp=None, rintp=None,
                  delta_offset_x=0, delta_offset_y=0):
        """Interpolate from the border fields to new coordinates

        Parameters
        ----------
        nintp: float or None
            Refractive index of the sphere
        rintp: float or None
            Radius of sphere [m]
        delta_offset_x: float
            Offset in x-direction [px]
        delta_offset_y: float
            Offset in y-direction [px]

        Returns
        -------
        phase_intp: 2D real-valued np.ndarray
            Interpolated phase at the given parameters

        Notes
        -----
        Not all combinations are poosible, e.g.

        - One of nintp or rintp must be None
        - The current interpolation range must include the values
          for rintp and nintp
        """
        if nintp is None:
            nintp = self.sphere_index

        if rintp is None:
            rintp = self.radius

        assert (rintp == self.radius or nintp ==
                self.sphere_index), "Only r or n can be changed at a time."
        assert rintp >= self.radius - self.dr
        assert rintp <= self.radius + self.dr
        assert nintp >= self.sphere_index - \
            self.dn, "Out of range: {} !> {}".format(
                nintp, self.sphere_index - self.dn)
        assert nintp <= self.sphere_index + self.dn

        left = self.get_border_phase(0, 0)
        if rintp == self.radius:
            dist = nintp - self.sphere_index
            dmax = self.dn
            if dist < 0:
                righ = self.get_border_phase(-1, 0)
            else:
                righ = self.get_border_phase(1, 0)
        else:
            dist = rintp - self.radius
            dmax = self.dr
            if dist < 0:
                righ = self.get_border_phase(0, -1)
            else:
                righ = self.get_border_phase(0, 1)

        # make dist positive so that we are interpolating from left to right
        dist = np.abs(dist)
        # perform linear interpolation of data.
        phas = left + (righ - left) * dist / dmax

        # interpolation of lateral movement
        ti = time.time()
        ipphas = spintp.RectBivariateSpline(np.arange(phas.shape[0]),
                                            np.arange(phas.shape[1]),
                                            phas)

        if delta_offset_x != 0 or delta_offset_y != 0:
            # Shift the image. The offset values used here
            # are not self.posx_offset and self.posy_offset!
            # The offset values are added to the fields computed
            # with self.posx_offset and self.posy_offset.
            newx = np.arange(phas.shape[0]) + delta_offset_x
            newy = np.arange(phas.shape[1]) + delta_offset_y
            phas = ipphas(newx, newy)
        if self.verbose > 2:
            print("Interpolation time for {}: {}".format(
                  self.model, time.time() - ti))

        return phas + self.pha_offset
