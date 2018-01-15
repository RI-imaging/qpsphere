import numpy as np

import qpsphere


def test_basic():
    r = 5e-6
    n = 1.339
    c = (11, 11)
    qpi = qpsphere.simulate(radius=r,
                            sphere_index=n,
                            medium_index=1.333,
                            wavelength=550e-9,
                            grid_size=(25, 25),
                            model="projection",
                            center=c)

    # fit simulation with projection model
    n_fit, r_fit, c_fit, qpi_fit = qpsphere.analyze(qpi=qpi,
                                                    r0=r * .8,
                                                    method="image",
                                                    model="projection",
                                                    ret_center=True,
                                                    ret_qpi=True)

    assert np.abs(n - n_fit) < 4e-6
    assert np.abs(r - r_fit) < 1.5e-9
    assert np.abs(c[0] - c_fit[0]) < 2.5e-3
    assert np.abs(c[1] - c_fit[1]) < 2.5e-3
    assert np.allclose(qpi.pha, qpi_fit.pha, atol=0.0026, rtol=0)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()