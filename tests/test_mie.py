import numpy as np

from qpsphere.models import mie


def test_basic():
    data = np.array([0.61718511, 0.63344636, 0.39500855,
                     0.62834482, 0.5612372, 0.24405929,
                     0.39808633, 0.24597916, -0.00504312])

    qpi = mie(grid_size=(3, 3),
              center=(0, 0),
              pixel_size=2e-6)
    assert np.allclose(data, qpi.pha.flatten())


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
