import warnings

import numpy as np

from qpsphere.models import _bhfield as bh


def test_default_simulation():
    data = np.array([0.99915 + 0.0059473j, 1.01950 - 0.0067643j,
                     1.01950 - 0.0067643j, 0.99915 + 0.0059473j,
                     1.02340 - 0.0037607j, 0.97630 + 0.4906j,
                     0.97630 + 0.4906j, 1.02340 - 0.0037607j,
                     1.02340 - 0.0037607j, 0.97630 + 0.4906j,
                     0.97630 + 0.4906j, 1.02340 - 0.0037607j,
                     0.99915 + 0.0059473j, 1.01950 - 0.0067643j,
                     1.01950 - 0.0067643j, 0.99915 + 0.0059473j])

    field = bh.simulate_sphere(shape_grid=(4, 4))
    assert np.allclose(field.flatten(), data)


def test_force_arp_warning():
    with warnings.catch_warnings(record=True) as rw:
        bh.simulate_sphere(radius_sphere_um=7,
                           refractive_index_sphere=1.5,
                           size_simulation_um=(20, 20),
                           shape_grid=(4, 4),
                           arp=False)
        msg = str(rw[0].message).lower()
        assert msg.count("bhfield")
        assert msg.count("standard precision failed")
        assert msg.count("retrying with arbitrary precision")


def test_get_binary():
    path1 = bh.fetch.get_binary(arp=False)
    path2 = bh.fetch.get_binary(arp=True)
    assert path1.exists()
    assert path2.exists()


def test_known_fail():
    try:
        bh.simulate_sphere(radius_sphere_um=50,
                           size_simulation_um=(70, 70),
                           shape_grid=(4, 4))
    except bh.wrap.BHFIELDExecutionError:
        pass
    else:
        assert False, "This simulation should not work with BHFIELD"


def test_shape():
    f1 = bh.simulate_sphere(shape_grid=(1, 4))
    f2 = bh.simulate_sphere(shape_grid=(4, 1))
    assert f1.shape == (1, 4)
    assert f2.shape == (4, 1)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
