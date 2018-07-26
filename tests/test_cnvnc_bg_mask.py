import numpy as np

import qpsphere


def test_mask_basic():
    qpi = qpsphere.simulate(radius=5e-6,
                            sphere_index=1.339,
                            medium_index=1.333,
                            wavelength=550e-9,
                            model="projection",
                            grid_size=(80, 80))

    mask = qpsphere.cnvnc.bg_phase_mask_from_sim(sim=qpi,
                                                 radial_clearance=1.0)

    assert np.all(qpi.pha[mask] == 0)
    assert np.all(qpi.pha[~mask] != 0)


def test_mask_offcenter():
    qpi = qpsphere.simulate(radius=5e-6,
                            sphere_index=1.339,
                            medium_index=1.333,
                            wavelength=550e-9,
                            model="projection",
                            grid_size=(80, 80),
                            center=(50, 80))

    mask = qpsphere.cnvnc.bg_phase_mask_from_sim(sim=qpi,
                                                 radial_clearance=1.0)

    assert np.all(qpi.pha[mask] == 0)
    assert np.all(qpi.pha[~mask] != 0)


def test_mask_from_qpi():
    qpi = qpsphere.simulate(radius=5e-6,
                            sphere_index=1.339,
                            medium_index=1.333,
                            wavelength=550e-9,
                            model="projection",
                            grid_size=(30, 30),
                            center=(20, 30))

    mask = qpsphere.cnvnc.bg_phase_mask_for_qpi(qpi=qpi,
                                                r0=qpi["sim radius"],
                                                method="image",
                                                model="projection",
                                                radial_clearance=1.0)

    # this good result may actually be a coincidence
    assert np.all(qpi.pha[mask] == 0)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
