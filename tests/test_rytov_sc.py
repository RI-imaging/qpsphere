import numpy as np

from qpsphere.models import excpt, mod_rytov_sc, mod_rytov


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


def test_basic():
    kwargs = dict(grid_size=(20, 20),
                  center=(9.5, 9.5),
                  radius=5e-6,
                  sphere_index=1.339,
                  medium_index=1.333,
                  wavelength=550e-9,
                  pixel_size=1e-6)

    kwargs2 = kwargs.copy()
    kwargs2["radius"], kwargs2["sphere_index"] = \
        mod_rytov_sc.correct_rytov_sc_input(
            radius_sc=kwargs["radius"],
            sphere_index_sc=kwargs["sphere_index"],
            medium_index=kwargs["medium_index"],
            radius_sampling=42)

    qpi = mod_rytov.rytov(**kwargs2)
    qpi_sc = mod_rytov_sc.rytov_sc(**kwargs)

    assert qpi_sc["sim model"] == "rytov-sc"
    assert np.all(qpi.pha == qpi_sc.pha)


def test_unsupported_parameters():
    kwargs = dict(grid_size=(20, 20),
                  center=(9.5, 9.5),
                  radius=5e-6,
                  sphere_index=1.330,
                  medium_index=1.333,
                  wavelength=550e-9,
                  pixel_size=1e-6)
    try:
        mod_rytov_sc.rytov_sc(**kwargs)
    except excpt.UnsupportedModelParametersError:
        pass
    else:
        assert False, "Sphere index lower than medium should error out"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
