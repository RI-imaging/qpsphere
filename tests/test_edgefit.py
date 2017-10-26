from os.path import abspath, dirname
import sys

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpsphere  # noqa: E402


def test_average_sphere_crop():
    radius = 1.01
    hcenter = 2 * radius
    hquarter = 2 * np.sqrt(radius**2 - 1)
    data = np.zeros((5, 5), dtype=float)
    data[2, 2] = 7
    pquarter = 7 * hquarter / hcenter  # ideal sphere
    data[1, 2] = data[3, 2] = data[2, 1] = data[2, 3] = pquarter

    avg, crop = qpsphere.edgefit.average_sphere(image=data,
                                                center=(2, 2),
                                                radius=radius,
                                                weighted=True,
                                                ret_crop=True)
    assert np.all((data == 0) == (crop == 0))
    assert np.allclose(crop[crop != 0], avg)


def test_average_sphere_even():
    radius = 1.01
    hcenter = 2 * radius
    # hquarter is located at the center of the adjacent pixels
    hquarter = 2 * np.sqrt(radius**2 - 2 * .5**2)
    data = np.zeros((4, 4), dtype=float)
    pquarter = 7 * hquarter / hcenter  # ideal sphere
    data[1, 1] = data[1, 2] = data[2, 1] = data[2, 2] = pquarter

    avg = qpsphere.edgefit.average_sphere(image=data,
                                          center=(1.5, 1.5),
                                          radius=radius,
                                          weighted=True,
                                          ret_crop=False)
    assert np.allclose(avg, 7 / (2 * radius))


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


def test_contour_canny_basic():
    size = 21
    cx = 10
    cy = 10
    radius = 7
    data = np.zeros((size, size), dtype=float)
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    data[r <= radius] = 1
    # perform edge detection
    edge = qpsphere.edgefit.contour_canny(image=data,
                                          radius=radius * .9)
    # this might differ from implementation to implementation
    assert np.sum(edge) == 56
    # the edge fully contains `data`
    assert np.allclose(r[edge].max(), 7.2801098892805181)


def test_circle_fit():
    data = np.zeros((7, 7), dtype=bool)
    data[3, 5] = data[1, 3] = data[3, 1] = data[5, 3] = True
    (cx, cy), r, dev = qpsphere.edgefit.circle_fit(data, ret_dev=True)
    assert np.allclose(cx, 3)
    assert np.allclose(cy, 3)
    assert np.allclose(r, 2)
    assert np.allclose(dev, 0, rtol=0, atol=3e-8)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
