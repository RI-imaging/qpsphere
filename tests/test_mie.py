import numpy as np

from qpsphere.models import mod_mie


def test_basic():
    data = np.array([0.61718511, 0.63344636, 0.39500855,
                     0.62834482, 0.5612372, 0.24405929,
                     0.39808633, 0.24597916, -0.00504312])

    qpi = mod_mie.mie(grid_size=(3, 3),
                      center=(0, 0),
                      pixel_size=2e-6)
    assert np.allclose(data, qpi.pha.flatten())


def test_field2ap_corr():
    phase = np.ones((50, 50)) * .21
    field = np.exp(1j*phase)
    assert np.allclose(phase, mod_mie.field2ap_corr(field)[1])
    assert np.allclose(phase, mod_mie.field2ap_corr(field * np.exp(2j * np.pi))[1])


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
