"""BHFIELD sphere wrapper"""
import os
import pathlib
import subprocess as sp
import tempfile
import warnings

import numpy as np

from .fetch import get_binary


class BHFIELDExecutionError(BaseException):
    """Raised when BHFIELD fails"""
    pass


def clear_temp(wdir, rmdir=True):
    """Remove all files in wdir"""
    wdir = pathlib.Path(wdir)
    extensions = ["*.log", "*.dat", "*.txt"]

    for ext in extensions:
        for ff in wdir.glob(ext):
            ff.unlink()

    if rmdir:
        wdir.rmdir()


def load_field(wdir, shape_grid):
    """Extract electric field from simulation file "V_0Ereim.dat"

    Parameters
    ----------
    wdir: str or pathlib.Path
        path to the working directory
    shape_grid: tuple of ints
        the shape of the simulation data grid

    Notes
    -----
    These are the files present in the working directory

    bhfield.log:
        log file containing scattering coeffs etc
        (as well as definitions of the output fields)

    bhdebug.log:
        extra information (checking roundoff errors etc)

    E_0allf.dat:
        E2 = EFSQ[dimensionless] = (relative) squared amplitude
        of complex E-field; Ec*(Ec^*) / E0**2

    E_1core.dat:
        E2 inside the core

    E_2coat.dat:
        E2 inside the coating

    E_3exte.dat:
        E2 at the outside of the sphere

    U_*.dat:
        U = UABS[F m-1 s-1] is the (relative) absorbed energy per
        unit volume and time; Ua [W m-3] / E0**2

    EU_zax.txt:
        E2(0,0,z) and U(0,0,z) along z-axis; it may be blank if
        the grid does not include such points

    V_0Eelli.dat:
        vector electric field; vibration ellipse (major & minor axes),
        ellipticity, azimuth[deg], p-a angle (phi)[deg], handedness
        angle[deg] & handedness

    V_0Ereim.dat: vector electric field;
        snapshots [Re (t=0), Im (t=period/4)]

    V_0Helli.dat:
        vector magnetic field; vibration ellipse (major & minor axes),
        ellipticity, azimuth[deg], p-a angle (phi)[deg],
        E-&H-phase dif[deg], handedness angle[deg] & handedness

    V_0Hreim.dat: vector magnetic field;
        snapshots [Re (t=0), Im (t=period/4)]

    V_0Poynt.dat:
        Poynting vector <S>, EH angle, optical irradiance (intensity)
        (norm<S>), I(plane), -div<S> (1st-3rd), UABS & DIVSR

    V_1*.dat:
        vector fields inside the core

    V_2*.dat:
        vector fields inside the coating

    V_3*.dat:
        vector fields at the outside of the sphere
    """
    wdir = pathlib.Path(wdir)
    check_simulation(wdir)
    field_file = wdir / "V_0Ereim.dat"

    a = np.loadtxt(str(field_file))

    assert shape_grid[0] == int(
        shape_grid[0]), "resulting x-size is not an integer"
    assert shape_grid[1] == int(
        shape_grid[1]), "resulting y-size is not an integer"

    Ex = a[:, 3] + 1j * a[:, 6]
    # Ey = a[:,4] + 1j*a[:,7]
    # Ez = a[:,5] + 1j*a[:,8]

    Exend = Ex.reshape((shape_grid[1], shape_grid[0])).transpose()
    return Exend


def simulate_sphere(radius_sphere_um=2.5,
                    size_simulation_um=[7, 7],
                    shape_grid=(50, 50),
                    refractive_index_medium=1.0,
                    refractive_index_sphere=1.01,
                    measurement_position_um=2.5,
                    wavelength_nm=500,
                    offset_x_um=0,
                    offset_y_um=0,
                    arp=True):
    """
    Parameters
    ----------
    radius_sphere_um : float
        radius of sphere in um
    size_simulation_um : list of floats
        Size of simulation volume in lateral dimension in um.
        If a float is given, then a square simulation size is assumed. If
        a tuple is given, then a rectangular shape is assumed.
    shape_grid : tuple of ints
        grid points in each lateral dimension.
        If a float is given, then a square simulation size is assumed. If
        a tuple is given, then a rectangular shape is assumed.
    refractive_index : float
        RI of sphere
    measurement_position_um : float
        axial measurement position in um
    wavelength_nm : float
        light wavelength in nanometers
    offset_x_um : float
        x coordinate of center of the sphere in um
    offset_y_um : float
        y coordinate of center of the sphere in um
    arp: bool
        Use arbitrary precision
    """
    wavelength_um = wavelength_nm / 1000

    # size simulation tuple
    sizeum = list(size_simulation_um)
    shape_grid = list(shape_grid)

    # The size of the simulation must be zero
    # if there is only one grid point.
    if shape_grid[0] == 1:
        sizeum[0] = 0
    if shape_grid[1] == 1:
        sizeum[1] = 0

    assert np.allclose(shape_grid[0], int(
        shape_grid[0])), "resulting x-size is not an integer"
    assert np.allclose(shape_grid[1], int(
        shape_grid[1])), "resulting y-size is not an integer"

    while True:
        # create temp dir
        wdir = tempfile.mkdtemp(prefix="qpsphere_bhfield_")

        try:
            run_simulation(wdir=wdir,
                           arp=arp,
                           wl=wavelength_um,
                           r_core=radius_sphere_um,
                           r_coat=radius_sphere_um,
                           n_grid_x=int(shape_grid[0]),
                           xspan_min=-sizeum[0] / 2 - offset_x_um,
                           xspan_max=sizeum[0] / 2 - offset_x_um,
                           n_grid_y=int(shape_grid[1]),
                           yspan_min=-sizeum[1] / 2 - offset_y_um,
                           yspan_max=sizeum[1] / 2 - offset_y_um,
                           n_grid_z=1,
                           zspan_min=measurement_position_um,
                           zspan_max=measurement_position_um,
                           case="other",
                           Kreibig=0,
                           n_med=refractive_index_medium,
                           n_core=refractive_index_sphere,
                           k_core=0,
                           n_coat=refractive_index_medium,
                           k_coat=0)
        except BaseException:
            if arp:
                raise
            else:
                msg = "bhfield: Standard precision failed. " \
                      + "Retrying with arbitrary precision."
                warnings.warn(msg)
                arp = True
            clear_temp(wdir=wdir)
        else:
            break

    result = load_field(wdir=wdir, shape_grid=shape_grid)
    clear_temp(wdir=wdir)

    return result


def run_simulation(wdir, arp=True, **kwargs):
    """
    Example
    -------
    100-nm silica sphere with 10-nm thick Ag coating,
    embedded in water; arprec 20 digits; illuminated with YAG (1064nm);
    scan xz plane (21x21, +-200nm)

    bhfield-arp-db.exe mpdigit wl r_core r_coat
                       n_grid_x xspan_min xspan_max
                       n_grid_y yspan_min yspan_max
                       n_grid_z zspan_min zspan_max
                       case  Kreibig
                       [n_med n_core k_core n_coat k_coat (case=other)]

    bhfield-arp-db.exe 20 1.064 0.050 0.060
                       21 -0.2 0.2
                       1 0 0
                       21 -0.2 0.2
                       other 0
                       1.3205 1.53413 0 0.565838 7.23262


    Explanation of parameters
    -------------------------
    mpdigit:
        arprec's number of precision digits;
        increase it to overcome round-off errors
    wl[um]:
        light wavelength in vacuum
    r_core[um], r_coat[um]:
        core & coat radii
    n_grid_x xspan_min[um] xspan_max[um]:
        number & span of grid points for field computation; x span
    n_grid_y yspan_min[um] yspan_max[um]:
        y span
    n_grid_z zspan_min[um] zspan_max[um]:
        z span
    Kreibig:
        Kreibig mean free path correction for Ag (0.0 - 1.0)
    case:
        nanoshell/liposome/HPC/barber/other
    n_med n_core k_core n_coat k_coat (case=other only):
        refractive indices of medium (real), core & coat (n, k)


    If `case=other`, complex refractive indices
    (n, k at the particular wavelength) must be specified.
    Otherwise (case = nanoshell etc) the medium/core/coat
    materials are predefined and the n,k values
    are taken from the data file (Ag_palik.nk etc).
    The latter reflects our own interest and is intended
    for use in our lab, so general users may not find it useful :-)
    """
    wdir = pathlib.Path(wdir)
    cmd = "{pathbhfield} {mpdigit} {wl:f} {r_core:f} {r_coat:f} " \
          + "{n_grid_x:d} {xspan_min:f} {xspan_max:f} " \
          + "{n_grid_y:d} {yspan_min:f} {yspan_max:f} " \
          + "{n_grid_z:d} {zspan_min:f} {zspan_max:f} " \
          + "{case} {Kreibig:f} {n_med:f} {n_core:f} {k_core:f} " \
          + "{n_coat:f} {k_coat:f}"
    old_dir = pathlib.Path.cwd()
    os.chdir(str(wdir))

    kwargs["pathbhfield"] = get_binary(arp=arp)

    if arp:
        kwargs["mpdigit"] = 16
    else:
        kwargs["mpdigit"] = ""

    # run simulation with kwargs
    sp.check_output(cmd.format(**kwargs), shell=True)

    # Go back to orgignal directory before checking (checking might fail)
    os.chdir(str(old_dir))

    # Check bhdebug.txt to make sure that you specify enough digits to
    # overcome roundoff errors.
    check_simulation(wdir)


def check_simulation(wdir):
    """
    Check bhdebug.txt to make sure that you specify enough digits to
    overcome roundoff errors.
    """
    wdir = pathlib.Path(wdir)
    field = wdir / "V_0Ereim.dat"
    if not (field.exists() and
            field.stat().st_size > 130):
        msg = "Output {} does not exist or is too small!".format(field)
        raise BHFIELDExecutionError(msg)
