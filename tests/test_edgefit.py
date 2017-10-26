from os.path import abspath, dirname
import sys

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpsphere  # noqa: E402


def test_circle_fit():
    data = np.zeros((7, 7), dtype=bool)
    data[3, 5] = data[1, 3] = data[3, 1] = data[5, 3] = True
    (cx, cy), r, dev = qpsphere.edgefit.circle_fit(data, ret_dev=True)
    assert np.allclose(cx, 3)
    assert np.allclose(cy, 3)
    assert np.allclose(r, 2)
    assert np.allclose(dev, 0, rtol=0, atol=3e-8)


def test_average_sphere_ideal():
    radius = 1.01
    hcenter = 2 * radius
    hquarter = 2 * np.sqrt(radius**2 - 1)
    data = np.zeros((5, 5), dtype=float)
    data[2, 2] = 7
    pquarter = 7 * hquarter / hcenter  # ideal sphere
    data[1, 2] = data[3, 2] = data[2, 1] = data[2, 3] = pquarter

    avg1 = qpsphere.edgefit.average_sphere(image=data,
                                           center=(2, 2),
                                           radius=radius,
                                           weighted=True,
                                           ret_crop=False)
    avg2 = qpsphere.edgefit.average_sphere(image=data,
                                           center=(2, 2),
                                           radius=radius,
                                           weighted=False,
                                           ret_crop=False)
    assert np.allclose(avg1, avg2), "expected an ideal sphere"
    assert np.allclose(avg1, 7 / (2 * radius)), "expected an ideal sphere"


def test_average_sphere_weighted():
    radius = 1.01
    data = np.zeros((5, 5), dtype=float)
    data[2, 2] = 7
    pquarter = 1  # not an ideal sphere
    data[1, 2] = data[3, 2] = data[2, 1] = data[2, 3] = pquarter

    avg1 = qpsphere.edgefit.average_sphere(image=data,
                                           center=(2, 2),
                                           radius=radius,
                                           weighted=True,
                                           ret_crop=False)
    avg2 = qpsphere.edgefit.average_sphere(image=data,
                                           center=(2, 2),
                                           radius=radius,
                                           weighted=False,
                                           ret_crop=False)
    assert not np.allclose(avg1, avg2), "expected no ideal sphere"
    exact = 7 / (2 * radius)
    assert abs(avg1 - exact) < (avg2 - exact), "weight reduces edge artifacts"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
