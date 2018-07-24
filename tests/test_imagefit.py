import pathlib
import tempfile
import shutil

import h5py
import numpy as np

import qpsphere
from qpsphere.imagefit import alg


def test_alg_export_phase():
    """when verbose>=2, then an """
    r = 5e-6
    n = 1.339
    s = 20
    qpi = qpsphere.simulate(radius=r,
                            sphere_index=n,
                            medium_index=1.333,
                            wavelength=550e-9,
                            grid_size=s,
                            model="projection",
                            pixel_size=3 * r / s)
    tdir = tempfile.mkdtemp(prefix="qpsphere_test_imagefit_alg_hdf5_")
    path = pathlib.Path(tdir) / "verbose_out.h5"
    n0 = n * 1.01
    r0 = r * 0.99
    alg.match_phase(qpi=qpi,
                    model="projection",
                    n0=n0,
                    r0=r0,
                    verbose=2,
                    verbose_h5path=path)

    with h5py.File(path, mode="r") as h5:
        groups = list(h5.keys())
        assert len(groups) == 1
        grp = h5[groups[0]]
        assert len(grp) > 3
        resk = list(grp.keys())[-1]
        ds = grp[resk]
        assert ds.shape == (s, s)
        assert ds.attrs["sim model"] == "projection"
        assert ds.attrs["radius initial"] == r0
        assert ds.attrs["index initial"] == n0
        assert ds.attrs["fit iteration"] == len(grp) - 1

    # cleanup
    shutil.rmtree(tdir, ignore_errors=True)


def test_alg_interim():
    r = 5e-6
    n = 1.339
    c = (11, 11)
    s = 25
    qpi = qpsphere.simulate(radius=r,
                            sphere_index=n,
                            medium_index=1.333,
                            wavelength=550e-9,
                            grid_size=(s, s),
                            model="projection",
                            pixel_size=3 * r / s,
                            center=c)

    # fit simulation with projection model
    _, _, interim = qpsphere.analyze(qpi=qpi,
                                     r0=r * .8,
                                     method="image",
                                     model="projection",
                                     imagekw={
                                         "ret_interim": True},
                                     )
    assert interim
    assert interim[0][0] == 0
    assert interim[1][0] == 1
    assert "radius" in interim[0][1]
    assert "sphere_index" in interim[0][1]
    assert "pha_offset" in interim[0][1]
    assert "center" in interim[0][1]


def test_alg_maxiter():
    r = 5e-6
    n = 1.339
    c = (11, 11)
    s = 25
    qpi = qpsphere.simulate(radius=r,
                            sphere_index=n,
                            medium_index=1.333,
                            wavelength=550e-9,
                            grid_size=(s, s),
                            model="projection",
                            pixel_size=3 * r / s,
                            center=c)

    # fit simulation with projection model
    _, _, num_iter = qpsphere.analyze(qpi=qpi,
                                      r0=r * .8,
                                      method="image",
                                      model="projection",
                                      imagekw={
                                          "min_iter": 1,
                                          "max_iter": 2,
                                          "ret_num_iter": True,
                                          "verbose": 1},
                                      )
    assert abs(num_iter) == 2, "max_iter is 2"
    assert np.sign(num_iter) == -1, "fitting aborted returns negative values"


def test_wrapper():
    r = 5e-6
    n = 1.339
    c = (11, 11)
    s = 25
    qpi = qpsphere.simulate(radius=r,
                            sphere_index=n,
                            medium_index=1.333,
                            wavelength=550e-9,
                            grid_size=(s, s),
                            model="projection",
                            pixel_size=3 * r / s,
                            center=c)

    # fit simulation with projection model
    n_fit, r_fit, c_fit, p_off, qpi_fit = qpsphere.analyze(qpi=qpi,
                                                           r0=r * .8,
                                                           method="image",
                                                           model="projection",
                                                           ret_center=True,
                                                           ret_qpi=True,
                                                           ret_pha_offset=True,
                                                           )
    assert np.abs(n - n_fit) < 3.7e-6
    assert np.abs(r - r_fit) < 1.3e-9
    assert np.abs(c[0] - c_fit[0]) < 2.7e-3
    assert np.abs(c[1] - c_fit[1]) < 2.7e-3
    assert p_off == 0
    assert np.allclose(qpi.pha, qpi_fit.pha, atol=0.0031, rtol=0)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
