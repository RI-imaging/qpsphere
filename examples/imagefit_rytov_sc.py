"""Rytov-SC image fit applied to a Mie simulation

This examples illustrates how the refractive index and radius of
a sphere can be determined accurately using the 2D phase fitting
algorithm with the systematically corrected Rytov approximation.
"""
import matplotlib.pylab as plt

import qpsphere

# run simulation with averaged Mie model
r = 5e-6
n = 1.360
med = 1.333
c = (125, 133)
qpi = qpsphere.simulate(radius=r,
                        sphere_index=n,
                        medium_index=med,
                        wavelength=550e-9,
                        grid_size=(256, 256),
                        model="mie-avg",
                        center=c)

# Fitting Mie simulations with the systematically corrected Rytov
# approximation (`model="rytov sc"`) yields lower parameter errors
# compared to the non-corrected Rytov approximation (`model="rytov"`).
n_fit, r_fit, c_fit, qpi_fit = qpsphere.analyze(qpi=qpi,
                                                r0=4e-6,
                                                method="image",
                                                model="rytov-sc",
                                                imagekw={"verbose": 1},
                                                ret_center=True,
                                                ret_qpi=True)

# plot results
fig = plt.figure(figsize=(8, 3.5))
txtkwargs = {"verticalalignment": "bottom",
             "horizontalalignment": "right",
             "fontsize": 12}

ax1 = plt.subplot(121, title="ground truth (Mie theory)")
map1 = ax1.imshow(qpi.pha)
plt.colorbar(map1, ax=ax1, fraction=.046, pad=0.04, label="phase [rad]")
t1 = "n={:.3f}\nmed={:.3f}\nr={:.1f}µm\ncenter=({:d},{:d})".format(
    n, med, r * 1e6, c[0], c[1])
ax1.text(1, 0, t1, transform=ax1.transAxes, color="w", **txtkwargs)

ax2 = plt.subplot(122, title="Rytov-SC fit residuals")
map2 = ax2.imshow(qpi.pha - qpi_fit.pha, vmin=-.5, vmax=.5, cmap="seismic")
plt.colorbar(map2, ax=ax2, fraction=.046, pad=0.04, label="phase error [rad]")
t2 = "Δn/n={:.2e}\nΔr/r={:.2e}\nΔx={:.2e}\nΔy={:.2e}".format(
    abs(n - n_fit) / n, abs(r - r_fit) / r,
    c_fit[0] - c[0], c_fit[1] - c[1])
ax2.text(1, 0, t2, transform=ax2.transAxes, color="k", **txtkwargs)

plt.tight_layout()
plt.show()
