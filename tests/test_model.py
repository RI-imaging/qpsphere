import numpy as np

import qpsphere


def test_basic_case1():
    """small radii"""
    qpi = qpsphere.simulate(radius=5e-6,
                            sphere_index=1.339,
                            medium_index=1.333,
                            wavelength=1064e-9)
    # Some of these tests may fail if the default parameters are changed
    assert qpi.shape == (80, 80)
    meta = {'pixel size': 2.5000000000000004e-07,
            'wavelength': 1.064e-06,
            'medium index': 1.333,
            'sim center': np.array([39.5, 39.5]),
            'sim radius': 5e-06,
            'sim index': 1.339
            }

    assert qpi["sim model"] == "projection"
    for key in meta:
        assert np.allclose(meta[key], qpi[key], rtol=0, atol=1e-15)


def test_basic_case2():
    """medium radii"""
    qpi = qpsphere.simulate(radius=5e-6,
                            sphere_index=1.339,
                            medium_index=1.333,
                            wavelength=550e-9)
    # Some of these tests may fail if the default parameters are changed
    assert qpi.shape == (80, 80)
    meta = {'pixel size': 1.9886363636363638e-07,
            'wavelength': 5.5e-07,
            'medium index': 1.333,
            'sim center': np.array([39.5, 39.5]),
            'sim radius': 5e-06,
            'sim index': 1.339}

    assert qpi["sim model"] == "projection"
    for key in meta:
        assert np.allclose(meta[key], qpi[key], rtol=0, atol=1e-15)


def test_basic_case3():
    """large radii"""
    qpi = qpsphere.simulate(radius=70e-6,
                            sphere_index=1.339,
                            medium_index=1.333,
                            wavelength=550e-9)
    # Some of these tests may fail if the default parameters are changed
    assert qpi.shape == (80, 80)
    meta = {'pixel size': 2.625e-06,
            'wavelength': 5.5e-07,
            'medium index': 1.333,
            'sim center': np.array([39.5, 39.5]),
            'sim radius': 7e-05,
            'sim index': 1.339,
            }

    assert qpi["sim model"] == "projection"
    for key in meta:
        assert np.allclose(meta[key], qpi[key], rtol=0, atol=1e-15)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
