import numpy as np

from qpsphere.models import projection


def test_basic():
    data = np.array([0.6854384, 0.62821467, 0.41126304,
                     0.62821467, 0.56522698, 0.30653737,
                     0.41126304, 0.30653737, 0.])

    qpi = projection(grid_size=(3, 3),
                     center=(0, 0),
                     pixel_size=2e-6)
    assert np.allclose(data, qpi.pha.flatten())


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
