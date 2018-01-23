import numpy as np

from qpsphere.models import mod_rytov_sc


def test_parameter_inversion():
    n, r = 1.45, 5.6e-6
    nmed = 1.333
    r_sc, n_sc = mod_rytov_sc.correct_rytov_output(radius=r,
                                                   sphere_index=n,
                                                   medium_index=1.333,
                                                   radius_sampling=42)
    assert r_sc < r
    assert n_sc > n

    r2, n2 = mod_rytov_sc.correct_rytov_sc_input(radius_sc=r_sc,
                                                 sphere_index_sc=n_sc,
                                                 medium_index=nmed,
                                                 radius_sampling=42)

    assert np.allclose(r, r2, atol=1e-15, rtol=0)
    assert np.allclose(n, n2, atol=1e-15, rtol=0)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
