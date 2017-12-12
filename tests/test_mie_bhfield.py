import numpy as np

from qpsphere.models import _bhfield as bh


def test_get_binary():
    path1 = bh.fetch.get_binary(arp=False)
    path2 = bh.fetch.get_binary(arp=True)
    assert path1.exists()
    assert path2.exists()


def test_default_simulation():
    data = np.array([0.99915+0.0059473j, 1.01950-0.0067643j,
                     1.01950-0.0067643j, 0.99915+0.0059473j,
                     1.02340-0.0037607j, 0.97630+0.4906j,
                     0.97630+0.4906j, 1.02340-0.0037607j,
                     1.02340-0.0037607j, 0.97630+0.4906j,
                     0.97630+0.4906j, 1.02340-0.0037607j,
                     0.99915+0.0059473j, 1.01950-0.0067643j,
                     1.01950-0.0067643j, 0.99915+0.0059473j])

    field = bh.simulate_sphere(size_grid=(4, 4))
    assert np.allclose(field.flatten(), data)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
