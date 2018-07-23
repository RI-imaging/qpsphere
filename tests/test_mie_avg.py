import numpy as np

from qpsphere.models import mie_avg


def test_basic():
    data = np.array([0.68567139, 0.6080693, 0.54356468,
                     0.6080693, 0.53277862, 0.47889313,
                     0.54356468, 0.47889313, 0.42260352])

    qpi = mie_avg(grid_size=(3, 3),
                  center=(0, 0),
                  pixel_size=2e-6)
    assert np.allclose(data, qpi.pha.flatten())


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
